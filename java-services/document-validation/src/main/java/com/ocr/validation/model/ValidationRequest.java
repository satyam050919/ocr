package com.ocr.validation.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ValidationRequest {
    private String documentId;
    private String documentType;
    private Map<String, AttributeValue> attributes;
    private boolean strictValidation;
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AttributeValue {
        private String value;
        private String type;
        private double confidence;
        private String extractionMethod;
    }
}
