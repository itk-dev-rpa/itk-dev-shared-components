"""This module is responsible for accessing emails using the Microsoft Graph API."""

from dataclasses import dataclass, field
import io

import requests
from bs4 import BeautifulSoup

from itk_dev_shared_components.graph.authentication import GraphAccess
from itk_dev_shared_components.graph.common import get_request


@dataclass
# pylint: disable-next=too-many-instance-attributes
class Email:
    """A class representing an email."""
    user: str
    id: str = field(repr=False)
    received_time: str
    sender: str
    receivers: list[str]
    subject: str
    body: str = field(repr=False)
    body_type: str
    has_attachments: bool

    def get_text(self) -> str:
        """Get the body as plain text.
        If the body is html it's converted to plaintext.
        If the body is text it's returned as is.

        Returns:
            str: The body as plain text.
        """
        if self.body_type == 'html':
            soup = BeautifulSoup(self.body, "html.parser")
            return soup.get_text().strip()

        return self.body


@dataclass
class Attachment:
    """A dataclass representing an email Attachment.
    It contains the graph id, name and size of the attachment.
    To get the actual data call graph.mail.get_attachment_data.
    """
    email: Email = field(repr=False)
    id: str = field(repr=False)
    name: str
    size: int


def get_emails_from_folder(user: str, folder_path: str, graph_access: GraphAccess) -> tuple[Email]:
    """Get all emails from the specified user and folder.
    You need to authorize against Graph to get the GraphAccess before using this function
    see the graph.authentication module.

    Args:
        user: The user who owns the folder.
        folder_path: The absolute path of the folder e.g. 'Inbox/Economy/May'
        graph_access: The GraphAccess object used to authenticate.

    Returns:
        tuple[Email]: The emails from the given folder.
    """
    folder_id = get_folder_id_from_path(user, folder_path, graph_access)

    endpoint = f"https://graph.microsoft.com/v1.0/users/{user}/mailFolders/{folder_id}/messages?$top=1000"

    response = get_request(endpoint, graph_access)
    emails_raw = response.json()['value']

    return _unpack_email_response(user, emails_raw)


def get_email_as_mime(email: Email, graph_access: GraphAccess) -> io.BytesIO:
    """Get an email as a file-like object in MIME format.

    Args:
        email: The email to get as MIME.
        graph_access: The GraphAccess object used to authenticate.

    Returns:
        io.BytesIO: A file-like object of the MIME file.
    """
    endpoint = f"https://graph.microsoft.com/v1.0/users/{email.user}/messages/{email.id}/$value"
    response = get_request(endpoint, graph_access)
    data = response.content
    return io.BytesIO(data)


def get_folder_id_from_path(user: str, folder_path: str, graph_access: GraphAccess) -> str:
    """Get the Graph id of a folder based on the path of the folder.
    You need to authorize against Graph to get the GraphAccess before using this function
    see the graph.authentication module.

    Args:
        user: The user who owns the folder.
        folder_path: The absolute path of the folder e.g. 'Inbox/Economy/May'
        graph_access: The GraphAccess object used to authenticate.

    Raises:
        ValueError: If a folder in the path can't be found.

    Returns:
        str: The UUID of the folder in Graph.
    """
    folders = folder_path.split("/")
    main_folder = folders[0]
    child_folders = folders[1:]

    folder_id = None

    # Get main folder
    endpoint = f"https://graph.microsoft.com/v1.0/users/{user}/mailFolders"
    response = get_request(endpoint, graph_access).json()
    folder_id = _find_folder(response, main_folder)
    if folder_id is None:
        raise ValueError(f"Top level folder '{main_folder}' was not found for user '{user}'.")

    # Get child folders
    for child_folder in child_folders:
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user}/mailFolders/{folder_id}/childFolders"
        folder_id = recursive_find_folder(endpoint, graph_access, child_folder)
        if folder_id is None:
            raise ValueError(f"Child folder '{child_folder}' not found under '{main_folder}' for user '{user}'.")

    return folder_id


def recursive_find_folder(endpoint: str, graph_access: GraphAccess, target_folder: str) -> str:
    """Look for target folder at endpoint, recursively going through pagination if available and necessary.

    Args:
        endpoint: Graph endpoint to lookup folder.
        graph_access: Access token for Graph API.
        target_folder: ID of target folder.

    Returns:
        Return folder ID.
    """
    response = get_request(endpoint, graph_access).json()
    folder_id = _find_folder(response, target_folder)

    if folder_id is None and '@odata.nextLink' in response:
        return recursive_find_folder(response['@odata.nextLink'], graph_access, target_folder)

    return folder_id


def list_email_attachments(email: Email, graph_access: GraphAccess) -> tuple[Attachment]:
    """List all attachments of the given email. This function only gets the id, name and size
    of the attachment. Use get_attachment_data to get the actual data of an attachment.

    Args:
        email: The email which attachments to list.
        graph_access: The GraphAccess object used to authenticate.

    Returns:
        tuple[Attachment]: A tuple of Attachment objects describing the attachments.
    """
    endpoint = f"https://graph.microsoft.com/v1.0/users/{email.user}/messages/{email.id}/attachments?$select=name,size,id"
    response = get_request(endpoint, graph_access).json()

    attachments = []
    for att in response['value']:
        attachments.append(Attachment(email, att['id'], att['name'], att['size']))

    return tuple(attachments)


def get_attachment_data(attachment: Attachment, graph_access: GraphAccess) -> io.BytesIO:
    """Get a file-like object representing the attachment.

    Args:
        attachment: The attachment to get.
        graph_access: The GraphAccess object used to authenticate.

    Returns:
        io.BytesIO: A file-like object representing the attachment.
    """
    email = attachment.email
    endpoint = f"https://graph.microsoft.com/v1.0/users/{email.user}/messages/{email.id}/attachments/{attachment.id}/$value"
    response = get_request(endpoint, graph_access)
    data_bytes = response.content
    return io.BytesIO(data_bytes)


def move_email(email: Email, folder_path: str, graph_access: GraphAccess, *, well_known_folder: bool = False) -> None:
    """Move an email to another folder under the same user.
    If well_known_folder is true, the folder path is assumed to be a well defined folder.
    See https://learn.microsoft.com/en-us/graph/api/resources/mailfolder?view=graph-rest-1.0
    for a list of well defined folder names.

    Args:
        email: The email to move.
        folder_path: The absolute path to the new folder. E.g. 'Inbox/Economy/May'
        graph_access: The GraphAccess object used to authenticate.
        well_known_folder: Whether the path is a 'well known folder'. Defaults to False.
    """
    if well_known_folder:
        folder_id = folder_path
    else:
        folder_id = get_folder_id_from_path(email.user, folder_path, graph_access)

    endpoint = f"https://graph.microsoft.com/v1.0/users/{email.user}/messages/{email.id}/move"

    token = graph_access.get_access_token()
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/json"
    }

    body = {
        'destinationId': folder_id
    }

    response = requests.post(
        url=endpoint,
        headers=headers,
        json=body,
        timeout=30
    )
    response.raise_for_status()

    new_id = response.json()['id']
    email.id = new_id


def delete_email(email: Email, graph_access: GraphAccess, *, permanent: bool = False) -> None:
    """Delete an email from the mailbox.
    If permanent is true the email is completely removed from the user's mailbox.
    If permanent is false the email is instead moved to the Deleted Items folder.

    Args:
        email: The email to delete.
        graph_access: The GraphAccess object used to authenticate.
        permanent: Whether to permanently remove the email or not. Defaults to False.
    """
    if permanent:
        endpoint = f"https://graph.microsoft.com/v1.0/users/{email.user}/messages/{email.id}"

        token = graph_access.get_access_token()
        headers = {'Authorization': f"Bearer {token}"}

        response = requests.delete(
            url=endpoint,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
    else:
        move_email(email, "deleteditems", graph_access, well_known_folder=True)


def _find_folder(response: dict, target_folder: str) -> str:
    """Find the target folder in

    Args:
        response: The json dict of the HTTP response.
        target_folder: The folder to find.

    Returns:
        str: The id of the target folder.
    """
    for g_folder in response['value']:
        if g_folder['displayName'] == target_folder:
            return g_folder['id']
    return None


def _unpack_email_response(user: str, emails_raw: list[dict[str, str]]) -> tuple[Email]:
    """Unpack a json HTTP response and create a list of Email objects.

    Args:
        user: The user who owns the email folder.
        json: The json dictionary created by response.json().

    Returns:
        tuple[Email]: A tuple of Email objects.
    """
    emails = []

    for email in emails_raw:
        mail_id = email['id']
        received_time = email['receivedDateTime']
        sender = email['from']['emailAddress']['address']
        receivers = [r['emailAddress']['address'] for r in email['toRecipients']]
        subject = email['subject']
        body = email['body']['content']
        body_type = email['body']['contentType']
        has_attachments = email['hasAttachments']

        emails.append(
            Email(
                user,
                mail_id,
                received_time,
                sender,
                receivers,
                subject,
                body,
                body_type,
                has_attachments
            )
        )

    return tuple(emails)
