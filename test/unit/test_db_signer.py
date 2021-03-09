# import os
# import json
# import unittest
# from mist.sdk.db import db
#
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import padding, utils
# from cryptography.hazmat.primitives.serialization import pkcs12
#
#
# class SignerTest(unittest.TestCase):
#     PASSPHRASE = "passphrase"
#     INCLEAR_P12_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "clearkey.p12"))
#     PASSWD_P12_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "passwdkey.p12"))
#     NONEXISTENT_PATH = "non/existent/database"
#     TESTDATAFILE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "testdatafile.db"))
#     TESTDATAFILE_DB_SHA256_HEX = "6e7c59d89ba4e63dbab463944146de74d88524a43e8035d337a46041e5858ef7"
#
#
#     def test_returns_None_when_no_database_path(self):
#
#         self.assertEqual(db.sign(), None)
#
#     def test_returns_None_when_empty_database_path(self):
#
#         self.assertEqual(db.sign(), None)
#
#     def test_throws_exception_when_nonexistent_path_given(self):
#         db.db_path = SignerTest.NONEXISTENT_PATH
#
#         with self.assertRaisesRegex(Exception, f"Database file not found: {SignerTest.NONEXISTENT_PATH}"):
#             db.sign()
#
#     def test_returns_basic_document_when_no_keys_given(self):
#         db.db_path = SignerTest.TESTDATAFILE_DB_PATH
#
#         ret = json.loads(db.sign())
#
#         self.assertEqual(ret["URI"], SignerTest.TESTDATAFILE_DB_PATH)
#         #self.assertEqual(ret["tsDoc"]["ts"], "")
#         self.assertEqual(ret["tsDoc"]["digest"], SignerTest.TESTDATAFILE_DB_SHA256_HEX)
#         self.assertEqual(ret["signCert"], None)
#         self.assertEqual(ret["signAlg"], None)
#         self.assertEqual(ret["signature"], None)
#
#     def test_throws_exception_when_nonexistent_path_given(self):
#         db.db_path = SignerTest.TESTDATAFILE_DB_PATH
#
#         with self.assertRaisesRegex(Exception, f"PKCS#12 file not found: {SignerTest.NONEXISTENT_PATH}"):
#             db.sign(pkcs12_path=SignerTest.NONEXISTENT_PATH)
#
#     def test_throws_exception_when_passwd_is_not_given(self):
#         db.db_path = SignerTest.TESTDATAFILE_DB_PATH
#
#         with self.assertRaisesRegex(ValueError, "Invalid password or PKCS12 data"):
#             db.sign(pkcs12_path=SignerTest.PASSWD_P12_PATH)
#
#     def test_returns_full_document_when_p12_and_passwd_are_given(self):
#         db.db_path = SignerTest.TESTDATAFILE_DB_PATH
#
#         ret = json.loads(db.sign(pkcs12_path=SignerTest.PASSWD_P12_PATH, passphrase=SignerTest.PASSPHRASE))
#
#         self.assertEqual(ret["URI"], SignerTest.TESTDATAFILE_DB_PATH)
#         #self.assertEqual(ret["tsDoc"]["ts"], "")
#         self.assertEqual(ret["tsDoc"]["digest"], SignerTest.TESTDATAFILE_DB_SHA256_HEX)
#         self.assertEqual(ret["signCert"], "")
#         self.assertEqual(ret["signAlg"], "SHA256WithRSASignature")
#         #self.assertEqual(ret["signature"], None)
#
#         validate_signature(ret["signature"], json.dumps(ret["tsDoc"]), SignerTest.PASSWD_P12_PATH, SignerTest.PASSPHRASE)
#
# def validate_signature(signature: str, message:str, pkcs12_path: str, passphrase:str):
#
#     with open(pkcs12_path, "rb") as f:
#         p12 = pkcs12.load_key_and_certificates(f.read(), bytes(passphrase, "utf-8"))
#
#     priv_key = p12[0]       # Private key
#     certificate = p12[1]    # Certificate
#     pubKey = certificate.public_key()
#
#     msg = bytes(message, "utf-8")
#     sign = bytes.fromhex(signature)
#
#     pubKey.verify(sign, msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
