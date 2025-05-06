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
public class ValidationRule {
    private String id;
    private String name;
    private String description;
    private String documentType;
    private String fieldName;
    private RuleType ruleType;
    private String pattern;
    private Double minValue;
    private Double maxValue;
    private List<String> allowedValues;
    private boolean required;
    private ValidationSeverity severity;
    private Double confidenceThreshold;
    
    public enum RuleType {
        REGEX,
        LENGTH,
        RANGE,
        ENUM,
        DATE_FORMAT,
        PRESENCE,
        CUSTOM
    }
    
    public enum ValidationSeverity {
        HARDBLOCK,
        WARNING,
        INFO
    }
}
