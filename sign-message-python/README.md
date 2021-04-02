# Message Signing with OCI Vault Encryption Key

This function exists for the purpose of verifying a digitally signed messsge.  The message can be any text, JSON, or XML in nature.  The message is base64 encoded by the client, and this function calls the OCI KMS Crytpo service to produce a `signature`.  When the companion verify-signature function is invoked, it is able to re-calculate the same message digest (hash) that this function computes, and then verify that the provided signature (which this function returns) is valid. 

## Client Flow
The caller can take any file and create a base64-encoded string:
```bash
prompt> export INPUT=$(cat input.xml|base64)
```
Invoke the function like this, and it will return a `signature`:
```bash
prompt> echo '{"base64message":"${INPUT}"}'|fn -v invoke FunctionsApp sign-message-python
{
  "key_id": "ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva",
  "key_version_id": "ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq",
  "signature": "P8erJ54ducEPXRfS7h5noKUduZcK5IfX4rXiG7cxGfEmKn2A+XRq46YQnEbJd7EhJV4l/hmzknpJ6Tn3TblLwVMItxJhdd/M3yELcu1Ga42M3J3zGHDdgJ43iKUtD1XI7a6FZ5+e8A+iH88Ri1nRku0rT32bGI+5hPCNlnUdVFcy4vmwL8mRRStQKYFbfnH2o1E06fMFK1wP3x7mahXbHQ14B2sA6meRkeAXqPAQq4J6+79W2N9B6xUC7Bh76LTcwBERZMwzShCBLCVDVz6JCB1u4POtXkyRPv8BKzs6TqPy6P3Fs4E+KZVDYqd8ZmonKL6Qzb0oAAGKhVdgfUi8kQ==",
  "signing_algorithm": "SHA_224_RSA_PKCS_PSS"
}
```
In order to verify the signature, see the corresponding verification function:
- [verify-signature](../verify-signature-python)

### Configuring Generic Function
In order for this function to work, the following must be configured as function configs:
- key_ocid
- key_version_ocid
- signing_algorithm
- endpoint

These can be configed via OCI Console, or via the shell and FN command line:
```bash
prompt> fn config function FunctionsApp sign-message-python endpoint https://xxx-crypto.kms.us-ashburn-1.oraclecloud.com
prompt> fn config function FunctionsApp sign-message-python key_ocid "ocid1.key.oc1.xxx"
prompt> fn config function FunctionsApp sign-message-python signing_algorithm "SHA_224_RSA_PKCS_PSS"
prompt> fn config function FunctionsApp sign-message-python key_version_ocid ocid1.keyversion.oc1.xxx"
```
