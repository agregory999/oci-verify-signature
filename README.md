# Digital Signature Verification

This function exists for the purpose of verifying a digitally signed messsge.  The message can be any text, JSON, or XML in nature.  When produced, a similar API or CLI call instructs the OCI KMS Crytpo service to produce a `message digest` and `signature`.  These are then required and used by this function to validate that the signed message digest was produced by the same key.

In order to produce the message digest, use openSSL:
```
openssl dgst -binary -sha224 file.xml| openssl enc -base64
WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==
```

Then the OCI CLI or API is used to produce a signature:
```
oci --profile INTEGRATION kms crypto signed-data sign --key-id ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva --key-version-id ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq --message-type DIGEST --message "WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==" --signing-algorithm SHA_224_RSA_PKCS_PSS --endpoint https://bfqfhkltaaeuk-crypto.kms.us-ashburn-1.oraclecloud.com
{
  "data": {
    "key-id": "ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva",
    "key-version-id": "ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq",
    "signature": "UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw==",
    "signing-algorithm": "SHA_224_RSA_PKCS_PSS"
  }
}
```
The resulting digest and signature can then be uploaded (for example) to an object storage bucket as metadata:
```
oci --profile INTEGRATION os object put  --bucket-name DigitalSignatureBucket --file 0120\&AD19468263\&SH3A4956.03\&1.0\&2018-08-08\&09-21-42.xml --metadata '{"digest": "WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==", "signature": "UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw=="}'
```

Once the message is within OCI, the same digest can be reproduced using a function or other means.  With this digest and the supplied signature, the verification can occur, which is what this function accomplishes.  An example invocation:

```
echo '{"digest":"WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==","signature":"UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw=="}' |fn invoke FunctionsApp verify-signature

{
  "is_signature_valid": true
}
```

Unless true is returned, the message signature is either not supplied or not valid.

## Configuring the Function
Build the function like you would any other.  Deploy it and configure it with 4 configs.  These are:
- key_ocid
- key_version_ocid
- signing_algorithm
- endpoint

Here is the deployment and configuration as an example:
```bash
fn -v deploy --app FunctionsApp

fn config function FunctionsApp verify-signature key_ocid "ocid1.key.oc1.iad.bfqfhkltaaeuk.abuwcljsvls5p2jxws7rgg6rmv6wwhv4d2f3jwpy62moxqkj4zbxtdjdyeva"

fn config function FunctionsApp verify-signature signing_algorithm "SHA_224_RSA_PKCS_PSS"

fn config function FunctionsApp verify-signature key_version_ocid ocid1.keyversion.oc1.iad.bfqfhkltaaeuk.aumtmbmqgsiaa.abuwcljsrsaiwd7zsw4oouaiejiwk3jmahexmyizjkmkdxozxuwtqsauh5yq

fn config function FunctionsApp verify-signature endpoint https://bfqfhkltaaeuk-crypto.kms.us-ashburn-1.oraclecloud.com

```


