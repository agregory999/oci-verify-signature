package com.oracle.digitalsignature;

// Crypto
import java.io.ByteArrayInputStream;
import java.util.Base64;
import java.util.Iterator;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import javax.xml.crypto.dsig.Reference;

import javax.xml.crypto.dsig.XMLSignature;
import javax.xml.crypto.dsig.XMLSignatureFactory;
import javax.xml.crypto.dsig.dom.DOMValidateContext;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

// Oracle Functions
import com.oracle.bmc.auth.ResourcePrincipalAuthenticationDetailsProvider;
import com.oracle.bmc.secrets.*;
import com.oracle.bmc.secrets.model.Base64SecretBundleContentDetails;
import com.oracle.bmc.secrets.requests.GetSecretBundleRequest;
import com.oracle.bmc.secrets.responses.GetSecretBundleResponse;

public class VerifyFunction {

    // Secrets Client will require OCI
    private SecretsClient secretsClient = null;
    private String ociClientMessage;

    // Config Param - if exists and "true"
    boolean debug = ((System.getenv("DEBUG") != null && System.getenv("DEBUG").equals("true")) ? true : false);
    
    // Constructor gets Vaults client
    public VerifyFunction() {
        // OCI Access requires Resource Principals
        try {
            ResourcePrincipalAuthenticationDetailsProvider ip_provider
                = ResourcePrincipalAuthenticationDetailsProvider.builder().build();
            if (ip_provider != null) {
                secretsClient = new SecretsClient(ip_provider);
                ociClientMessage = "Got Secrets Client from Resource Principal";
                return;
            }
        } catch (Exception e) {
            ociClientMessage = "Unable to create vault client RPST";
        }

    }

    public static class Response {
        private boolean verified;
        private String detail;
        public boolean getVerified() {
            return verified;
        }
        public Response(boolean ver) {
            this.verified = ver;
        }

        public String getDetail() {
            return detail;
        }
        public void setDetail(String detail) {
            this.detail = detail;
        }
        public void setVerified(boolean verified) {
            this.verified = verified;
        }
    }

    public static class Input {
        private String xmlString;
        //private Base64
        private String base64InputXML;
        private String secretOcid;

        public void setXmlString(String xmlString) {
            this.xmlString = xmlString;
        }

        public String getXmlString() {
            return xmlString;
        }

        public void setSecretOcid(String secretOcid) {
            this.secretOcid = secretOcid;
        }

        public String getSecretOcid() {
            return secretOcid;
        }

        public String getBase64InputXML() {
            return base64InputXML;
        }

        public void setBase64InputXML(String base64InputXML) {
            this.base64InputXML = base64InputXML;
        }
    }

    public Response handleRequest(Input input) {


        // Set up response
        Response resp = new Response(false);
        XMLSignatureFactory fac = XMLSignatureFactory.getInstance("DOM");
        StringBuffer messages = new StringBuffer();

        // Get reference to Secrets Client otherwise fail
        if (secretsClient == null) {
            resp.setDetail("Could not get secrets client: " + ociClientMessage);
            return resp;
        }
 
        // Try to grab a secret "Shared Key"
        // Example "ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya75lqnccnnz2o3dbevgisus77qq653vsoyaxo7ke7ttea"
        try {

            // Check secretOcid
            if (input.getSecretOcid() == null) {
                resp.setDetail("Required input secredOcid not supplied");
                return resp;
            }

            // Get secret if there
            GetSecretBundleRequest getSecretRequest = GetSecretBundleRequest.builder().secretId(input.getSecretOcid()).build();
            GetSecretBundleResponse getSecretResponse = secretsClient.getSecretBundle(getSecretRequest);
            
            Base64SecretBundleContentDetails secretContent =  (Base64SecretBundleContentDetails) getSecretResponse.getSecretBundle().getSecretBundleContent();
            String decodedSecretKey = new String(Base64.getDecoder().decode(secretContent.getContent()));

            if (debug) messages.append("|Secret Found:" + decodedSecretKey);

            String inputXML = "";
            if (input.getBase64InputXML() != null) {
                // process Base64
                inputXML = new String(Base64.getDecoder().decode(input.getBase64InputXML()));
                if (debug) messages.append("XML from Base64:"+inputXML);
            }
            else if (input.getXmlString() == null) {
                inputXML = input.getXmlString();
                resp.setDetail("Required input xmlString not supplied");
                return resp;
            }
            // Pull XML Object from String
            //if (debug) messages.append("|Input XML: " + input.getXmlString());
            
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            dbf.setNamespaceAware(true);
            Document doc = dbf.newDocumentBuilder().parse(new ByteArrayInputStream(inputXML.getBytes("UTF-8")));

            //Grab NodeList for signature
            NodeList nl = doc.getElementsByTagNameNS(XMLSignature.XMLNS, "Signature");

            if (nl.getLength() == 0 ) {
                resp.setDetail(messages + "No digital signature found");
                return resp;
            } 
            else {
                // Verify the signature
                
                SecretKey hmacKey = new SecretKeySpec(decodedSecretKey.getBytes(), "HMAC");
                //SecretKey hmacKey = new SecretKeySpec(secretContent.getContent().getBytes(), "HMAC");
                DOMValidateContext valContext = new DOMValidateContext(hmacKey, nl.item(0));
                XMLSignature signature = fac.unmarshalXMLSignature(valContext);
                if (debug) {
                    messages.append("|XMLSig: " + signature.toString());
                    messages.append("|SigVal: " + signature.getSignatureValue().getValue());
                    messages.append("|Sig Method: " + signature.getSignedInfo().getSignatureMethod().getAlgorithm());
                }
                if (signature == null) {
                    resp.setDetail(messages + "|digital signature obj not created");
                    return resp;
                }

                // Check signature for type
                //signature.
                boolean coreValidity = signature.validate(valContext);

                // Failure to verify
                if (!coreValidity) {
                    // Only do this if we care to debug it
                    if (debug) {
                        messages.append("Signature failed core validation");
                        boolean sv = signature.getSignatureValue().validate(valContext);
                        messages.append("|Signature validation status: " + sv);
                        if (!sv) {
                            Iterator i = signature.getSignedInfo().getReferences().iterator();
                            for (int j = 0; i.hasNext(); ++j) {
                                Reference r = (Reference) i.next();
                                // Validate (all for debug)
                                boolean refValid = r.validate(valContext);
                                messages.append("|Ref "+ j + " Path: " + r.getURI());
                                messages.append("|Ref "+ j + " Digest: " + r.getDigestValue().toString());
                                messages.append("|Ref "+ j + " Calc Digest: " + r.getCalculatedDigestValue().toString());
                                messages.append("|Ref[" + j + "] validity status: " + refValid);
                                if (refValid) {
                                    messages.append("|Digest value is good but the Key is not matching : ref[" + j + "] validity status: " + refValid);
                                    
                                } else {
                                    messages.append("|Both Key and Digest value are not matching ref[" + j + "] validity status: " + refValid);
                                }
                            }
                        } else {
                            messages.append("|Key is good but Digest Value not matching. The xml data was changed or corrupted after Digital Signing");
                        }
                    }

                    // Return Failure
                    resp.setDetail(messages + "|Digital Signature found but failed.  Use DEBUG for more information.");
                    return resp;
                }

            }

            // If we got this far, it is all good
            resp.setVerified(true);
            resp.setDetail(messages + "|Digital signature VALID!!!");
            return resp;

        } catch (Exception e) {
            resp.setDetail("Messages: "+ messages + "|Error: " + e);
            return resp;
        }
     } // end handle call
} // end of class
