# Simple Python XML Signature Verification

This function exists for the purpose of verifying a digitally signed messsge.  The message can be any text, JSON, or XML in nature.  The message is used to produce a `digest`, and an OCI API or CLI call instructs the OCI KMS Crytpo service to produce a `signature`.  When the function is invoked, it is able to re-calculate the same message digest (hash) that the client used, and then verify that the provided signature is valid. 

## Client Flow
In order to produce the message digest, the client uses openSSL:
```bash
openssl dgst -binary -sha224 file.xml| openssl enc -base64
WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==
```
This message digest is used with the OCI CLI or API is used to produce a signature:
```bash
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
The resulting signature can then be added to an object storage bucket as metadata - note that the digest is explicly not sent, as the function will re-calculate the same hashed message digest:
```bash
oci --profile INTEGRATION os object put  --bucket-name DigitalSignatureBucket --file file.xml \
--metadata '{"signature": "UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw=="}'
```

## Function #1 -- Signature Verification (pass in digest and signature)
There is a generic function called verify-signature.  It requires an invocation with a message signature and a digest.  The function calls the OCI Crypto API and produces a verification response.  If successful, the response will look look like this:
```bash
prompt>  echo '{"digest":"WiiYYbUrBmSLvtnY3FM5o/CGgMPNh/TntFvdSA==","signature":"UESjYkFS1Uvkuy5ESmvwJ47YfJTOzD6PVcDqo35DwXSqWgP3OOC4L+xnGMtJT8qbsws8DC+I63FjkP9b7wPxV+FpjVTXTQYf+SwXvlK7zqWeXBoHjLlo5BcUnCMF+4S6kTcq7RNdh6YcCtODdZ8uncSY/RrenjaqyQrjdnVKvSaS25gkmew5m6scprt6ZakDbKUe/G98TL+KWtmSINlIng0oeJWMTaCYkFXNN8lV04wOfE5uCCXQXjhGuNTanvyig+cRbbfxoORa6nO8+y4ffquQ+kE4hLB5K4pMgridqpEEPBP45r3Kg5vjdGshnCbHuOcIigVUQWKf8JASgCVjZw=="}' |fn invoke FunctionsApp verify-signature

{
  "is_signature_valid": true
}
```
### Configuring Generic Function
In order for this function to work, the following must be configured as function configs:
- key_ocid
- key_version_ocid
- signing_algorithm
- endpoint

## Function #2 -- Event Flow (message put in bucket kicks it off)
The `verify-signature-event` function is designed to take in an OCI Event.  The event is generated based on the addition or update of an object in a bucket.  There are 2 buckets involved in the overall solution - one as the input bucket and exposed to clients (writable), and the other internal, where verified messages are put by the function.  Each time the input bucket is added to, the function takes that event, looks at the new message, calculates the (same) digest as the client, and uses the OCI Crypto API to verify the supplied signature.  If the verification is successful, the message is then put to the internal bucket, where it cane be trusted or acted upon.

### Diagram
![Diagram](images/DigitalSignatureFlow.svg)
