package com.ocr.validation.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ValidationResult {
    private String documentId;
    private String documentType;
    private boolean valid;
    private List<ValidationIssue> issues;
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ValidationIssue {
        private String fieldName;
        private String message;
        private ValidationRule.ValidationSeverity severity;
        private String ruleId;
        private String expectedValue;
        private String actualValue;
        private Double confidence;
    }
}
