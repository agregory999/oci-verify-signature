package com.oracle.digitalsignature;

import com.fnproject.fn.testing.*;
import org.junit.*;

import static org.junit.Assert.*;

public class VerifyFunctionTest {

    @Rule
    public final FnTestingRule testing = FnTestingRule.createDefault();

    // @Test
    // public void shouldRequireOcid() {
    //     testing.givenEvent().withBody("{}").enqueue();
    //     testing.thenRun(VerifyFunction.class, "handleRequest");

    //     FnResult result = testing.getOnlyResult();
    //     assertEquals("{\"verified\":false,\"detail\":\"Required input secredOcid not supplied\"}", result.getBodyAsString());
    // }

    // @Test
    // public void shouldRequireXML() {
    //     testing.givenEvent().withBody("{\"secretOcid\":\"ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya75lqnccnnz2o3dbevgisus77qq653vsoyaxo7ke7ttea\"}").enqueue();
    //     testing.thenRun(VerifyFunction.class, "handleRequest");

    //     FnResult result = testing.getOnlyResult();
    //     assertEquals("{\"verified\":false,\"detail\":\"Required input xmlString not supplied\"}", result.getBodyAsString());
    // }

}