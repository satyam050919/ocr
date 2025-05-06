package com.ocr.validation.service;

import com.ocr.validation.model.ValidationRequest;
import com.ocr.validation.model.ValidationResult;
import com.ocr.validation.model.ValidationRule;
import com.ocr.validation.repository.ValidationRuleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ValidationService {

    private final ValidationRuleRepository ruleRepository;

    public ValidationResult validateDocument(ValidationRequest request) {
        log.info("Validating document: {}", request.getDocumentId());
        
        List<ValidationRule> rules = ruleRepository.findByDocumentType(request.getDocumentType());
        List<ValidationResult.ValidationIssue> issues = new ArrayList<>();
        
        Map<String, List<ValidationRule>> rulesByField = rules.stream()
                .collect(Collectors.groupingBy(ValidationRule::getFieldName));
        
        for (Map.Entry<String, List<ValidationRule>> entry : rulesByField.entrySet()) {
            String fieldName = entry.getKey();
            List<ValidationRule> fieldRules = entry.getValue();
            
            ValidationRequest.AttributeValue attributeValue = request.getAttributes().get(fieldName);
            
            boolean fieldRequired = fieldRules.stream().anyMatch(ValidationRule::isRequired);
            if (fieldRequired && (attributeValue == null || attributeValue.getValue() == null || attributeValue.getValue().isEmpty())) {
                issues.add(createValidationIssue(
                    fieldName,
                    "Required field is missing",
                    ValidationRule.ValidationSeverity.HARDBLOCK,
                    fieldRules.stream().filter(ValidationRule::isRequired).findFirst().get().getId(),
                    "non-empty value",
                    "missing",
                    0.0
                ));
                continue;
            }
            
            if (attributeValue == null) {
                continue;
            }
            
            for (ValidationRule rule : fieldRules) {
                if (rule.getConfidenceThreshold() != null && 
                    attributeValue.getConfidence() < rule.getConfidenceThreshold()) {
                    issues.add(createValidationIssue(
                        fieldName,
                        "Confidence score below threshold",
                        rule.getSeverity(),
                        rule.getId(),
                        "confidence >= " + rule.getConfidenceThreshold(),
                        "confidence = " + attributeValue.getConfidence(),
                        attributeValue.getConfidence()
                    ));
                }
            }
            
            for (ValidationRule rule : fieldRules) {
                switch (rule.getRuleType()) {
                    case REGEX:
                        validateRegex(rule, attributeValue, fieldName, issues);
                        break;
                    case LENGTH:
                        validateLength(rule, attributeValue, fieldName, issues);
                        break;
                    case RANGE:
                        validateRange(rule, attributeValue, fieldName, issues);
                        break;
                    case ENUM:
                        validateEnum(rule, attributeValue, fieldName, issues);
                        break;
                    case DATE_FORMAT:
                        validateDateFormat(rule, attributeValue, fieldName, issues);
                        break;
                    case PRESENCE:
                        break;
                    case CUSTOM:
                        break;
                }
            }
        }
        
        boolean valid = issues.stream()
                .noneMatch(issue -> issue.getSeverity() == ValidationRule.ValidationSeverity.HARDBLOCK);
        
        if (request.isStrictValidation()) {
            valid = issues.isEmpty();
        }
        
        return ValidationResult.builder()
                .documentId(request.getDocumentId())
                .documentType(request.getDocumentType())
                .valid(valid)
                .issues(issues)
                .build();
    }
    
    private void validateRegex(ValidationRule rule, ValidationRequest.AttributeValue attributeValue, 
                              String fieldName, List<ValidationResult.ValidationIssue> issues) {
        if (rule.getPattern() != null && !Pattern.matches(rule.getPattern(), attributeValue.getValue())) {
            issues.add(createValidationIssue(
                fieldName,
                "Value does not match required pattern",
                rule.getSeverity(),
                rule.getId(),
                "pattern: " + rule.getPattern(),
                attributeValue.getValue(),
                attributeValue.getConfidence()
            ));
        }
    }
    
    private void validateLength(ValidationRule rule, ValidationRequest.AttributeValue attributeValue, 
                               String fieldName, List<ValidationResult.ValidationIssue> issues) {
        int length = attributeValue.getValue().length();
        if (rule.getMinValue() != null && length < rule.getMinValue()) {
            issues.add(createValidationIssue(
                fieldName,
                "Value length is too short",
                rule.getSeverity(),
                rule.getId(),
                "min length: " + rule.getMinValue(),
                "length: " + length,
                attributeValue.getConfidence()
            ));
        }
        if (rule.getMaxValue() != null && length > rule.getMaxValue()) {
            issues.add(createValidationIssue(
                fieldName,
                "Value length is too long",
                rule.getSeverity(),
                rule.getId(),
                "max length: " + rule.getMaxValue(),
                "length: " + length,
                attributeValue.getConfidence()
            ));
        }
    }
    
    private void validateRange(ValidationRule rule, ValidationRequest.AttributeValue attributeValue, 
                              String fieldName, List<ValidationResult.ValidationIssue> issues) {
        try {
            double value = Double.parseDouble(attributeValue.getValue());
            if (rule.getMinValue() != null && value < rule.getMinValue()) {
                issues.add(createValidationIssue(
                    fieldName,
                    "Value is below minimum",
                    rule.getSeverity(),
                    rule.getId(),
                    "min: " + rule.getMinValue(),
                    "value: " + value,
                    attributeValue.getConfidence()
                ));
            }
            if (rule.getMaxValue() != null && value > rule.getMaxValue()) {
                issues.add(createValidationIssue(
                    fieldName,
                    "Value is above maximum",
                    rule.getSeverity(),
                    rule.getId(),
                    "max: " + rule.getMaxValue(),
                    "value: " + value,
                    attributeValue.getConfidence()
                ));
            }
        } catch (NumberFormatException e) {
            issues.add(createValidationIssue(
                fieldName,
                "Value is not a number",
                rule.getSeverity(),
                rule.getId(),
                "numeric value",
                attributeValue.getValue(),
                attributeValue.getConfidence()
            ));
        }
    }
    
    private void validateEnum(ValidationRule rule, ValidationRequest.AttributeValue attributeValue, 
                             String fieldName, List<ValidationResult.ValidationIssue> issues) {
        if (rule.getAllowedValues() != null && !rule.getAllowedValues().contains(attributeValue.getValue())) {
            issues.add(createValidationIssue(
                fieldName,
                "Value is not in allowed list",
                rule.getSeverity(),
                rule.getId(),
                "one of: " + String.join(", ", rule.getAllowedValues()),
                attributeValue.getValue(),
                attributeValue.getConfidence()
            ));
        }
    }
    
    private void validateDateFormat(ValidationRule rule, ValidationRequest.AttributeValue attributeValue, 
                                   String fieldName, List<ValidationResult.ValidationIssue> issues) {
        if (rule.getPattern() != null && !Pattern.matches(rule.getPattern(), attributeValue.getValue())) {
            issues.add(createValidationIssue(
                fieldName,
                "Date format is invalid",
                rule.getSeverity(),
                rule.getId(),
                "format: " + rule.getPattern(),
                attributeValue.getValue(),
                attributeValue.getConfidence()
            ));
        }
    }
    
    private ValidationResult.ValidationIssue createValidationIssue(
            String fieldName, String message, ValidationRule.ValidationSeverity severity,
            String ruleId, String expectedValue, String actualValue, Double confidence) {
        return ValidationResult.ValidationIssue.builder()
                .fieldName(fieldName)
                .message(message)
                .severity(severity)
                .ruleId(ruleId)
                .expectedValue(expectedValue)
                .actualValue(actualValue)
                .confidence(confidence)
                .build();
    }
}
