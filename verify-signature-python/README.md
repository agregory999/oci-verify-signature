# Signature Verification with OCI Vault Encryption Key

This function is paired with the corresponding [sign-message-python](../sign-message-python) function.  It performs signature verification, given a base64-encoded message and a signature, which the other function generates.  The client will receive a response to indicate that the message is valid.  The function takes the base64-encoded string, computes a `digest`, which should be the same as the computed digest that the corresponding function generated.  If any part of the original file changed, the digest will not match, and the signature will not verify.

To invoke the function, get the message into a base64-encoded string:
```bash
prompt> export INPUT=$(cat input.xml|base64)
```

The `signature` that was previously generated is passed in, in addition to the base64-encoded message:
```bash
echo '{"signature":"al3q+jmWWC0jStNeENy/EiI02+DT+I2WwKPBzKYbnvDyiDHfPYKk7aeSjjFinGIP3dNSRMan+tm2lHGy/Iu5ZP8SSkC3OslZdCZ24F65Ruzqyuf3k34nbZH03ie69Rh5it5IJC3tktJruwgPJU6V0iDcW8JrcJF6NCHZv9FN/j4NOF8JMi2edXsbrnBw3H/dC1koDkr+93ApwWb/ZKhd/M3Mo/GkNZ0qDovGF0RpFDXor8XlFRbzJDQBr5xBpuai8pB20e3Pfby5/WPLgZKgA4idKFEHUBjmPp9t9UMev6OqUwWFTuEH6cRM+VmpGI/jghEas7haEvCnXte0LxVaaw==","base64message":"${INPUT}"}'|fn -v invoke FunctionsApp verify-signature
{
  "is_signature_valid": true
}
```
Errors calling the API or with signature verification will be reported in the output.

### Configuring Generic Function
In order for this function to work, the following must be configured as function configs:
- key_ocid
- key_version_ocid
- signing_algorithm
- endpoint

These can be configed via OCI Console, or via the shell and FN command line:
```bash
prompt> fn config function FunctionsApp verify-signature-python endpoint https://xxx-crypto.kms.us-ashburn-1.oraclecloud.com
prompt> fn config function FunctionsApp verify-signature-python key_ocid "ocid1.key.oc1.xxx"
prompt> fn config function FunctionsApp verify-signature-python signing_algorithm "SHA_224_RSA_PKCS_PSS"
prompt> fn config function FunctionsApp verify-signature-python key_version_ocid ocid1.keyversion.oc1.xxx"
```
