"""Tests relating to the graph.mail module."""

import unittest
import json
import os

from dotenv import load_dotenv

from itk_dev_shared_components.graph import authentication, mail

load_dotenv()


class EmailTest(unittest.TestCase):
    """Tests relating to the graph.mail module."""
    @classmethod
    def setUpClass(cls) -> None:
        # Get Graph credentials from the environment variables.
        credentials = json.loads(os.environ['GRAPH_API'])
        client_id = credentials['client_id']
        tenant_id = credentials['tenant_id']
        username = credentials['username']
        password = credentials['password']

        cls.graph_access = authentication.authorize_by_username_password(username, password, tenant_id=tenant_id, client_id=client_id)

        # Define mail user and folders
        cls.user = os.environ['MAIL_USER']
        cls.folder_prefix = os.environ['MAIL_FOLDER_PREFIX']
        cls.folder_count = os.environ['MAIL_FOLDER_COUNT']
        cls.folder1 = os.environ['MAIL_FOLDER1']
        cls.folder2 = os.environ['MAIL_FOLDER2']

    def test_correct_usage(self):
        """Test all functions relating to the mail part of Graph.
        Use a test email in the given users mailbox in the given folder.
        Delete email permanently is not tested.
        """
        # Get email from test folder
        emails = mail.get_emails_from_folder(self.user, self.folder1, self.graph_access)
        self.assertNotEqual(len(emails), 0, "No emails found in test folder!")
        self.assertEqual(len(emails), 1, "More than 1 email found in test folder!")
        email = emails[0]

        # Check more than 10 folders
        for i in range(int(self.folder_count)):
            mail.get_emails_from_folder(self.user, f"{self.folder_prefix}{i}", self.graph_access)

        # Check email subject and body
        self.assertEqual(email.subject, "Test subject")
        self.assertTrue(email.get_text().startswith("Test text"))

        # List attachments
        attachments = mail.list_email_attachments(email, self.graph_access)
        self.assertEqual(len(attachments), 3)

        # Get attachment object 'Test document.pdf'
        attachment = next((att for att in attachments if att.name == "Test document.pdf"), None)
        self.assertIsNotNone(attachment)

        # Get attachment file and read first 4 bytes
        file = mail.get_attachment_data(attachment, self.graph_access)
        self.assertEqual(file.read(4), b'%PDF')

        # Get email as MIME and read first 8 bytes
        file = mail.get_email_as_mime(email, self.graph_access)
        self.assertEqual(file.read(8), b'Received')

        # Move the email
        mail.move_email(email, self.folder2, self.graph_access)

        # Delete to deleted items folder
        mail.delete_email(email, self.graph_access)

        # Move email back
        mail.move_email(email, self.folder1, self.graph_access)

    def test_wrong_usage(self):
        """Test that raised errors actually get raised."""
        with self.assertRaises(ValueError):
            mail.get_folder_id_from_path(self.user, "Foo/Bar", self.graph_access)

        with self.assertRaises(ValueError):
            mail.get_folder_id_from_path(self.user, "Indbakke/FooBar", self.graph_access)


if __name__ == "__main__":
    unittest.main()
