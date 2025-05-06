package com.ocr.validation.repository;

import com.ocr.validation.model.ValidationRule;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class ValidationRuleRepository {
    
    private final Map<String, ValidationRule> rules = new HashMap<>();
    
    public ValidationRuleRepository() {
        addRule(createRule(
            "Passport Number",
            "passport",
            "passport_number",
            ValidationRule.RuleType.REGEX,
            "^[A-Z0-9]{6,9}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.8
        ));
        
        addRule(createRule(
            "Full Name",
            "passport",
            "full_name",
            ValidationRule.RuleType.LENGTH,
            null,
            2.0, 100.0, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Date of Birth",
            "passport",
            "date_of_birth",
            ValidationRule.RuleType.DATE_FORMAT,
            "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "MRZ Line 1",
            "passport",
            "mrz_line1",
            ValidationRule.RuleType.LENGTH,
            null,
            44.0, 44.0, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.6
        ));
        
        addRule(createRule(
            "MRZ Line 2",
            "passport",
            "mrz_line2",
            ValidationRule.RuleType.LENGTH,
            null,
            44.0, 44.0, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.6
        ));
        
        addRule(createRule(
            "Invoice Number",
            "invoice",
            "invoice_number",
            ValidationRule.RuleType.PRESENCE,
            null,
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Invoice Date",
            "invoice",
            "invoice_date",
            ValidationRule.RuleType.DATE_FORMAT,
            "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Total Amount",
            "invoice",
            "total_amount",
            ValidationRule.RuleType.PRESENCE,
            null,
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.8
        ));
        
        addRule(createRule(
            "License Number",
            "drivers_license",
            "license_number",
            ValidationRule.RuleType.PRESENCE,
            null,
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.8
        ));
        
        addRule(createRule(
            "Full Name",
            "drivers_license",
            "full_name",
            ValidationRule.RuleType.LENGTH,
            null,
            2.0, 100.0, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Date of Birth",
            "drivers_license",
            "date_of_birth",
            ValidationRule.RuleType.DATE_FORMAT,
            "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Expiry Date",
            "drivers_license",
            "expiry_date",
            ValidationRule.RuleType.DATE_FORMAT,
            "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Account Number",
            "utility_bill",
            "account_number",
            ValidationRule.RuleType.PRESENCE,
            null,
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Bill Date",
            "utility_bill",
            "bill_date",
            ValidationRule.RuleType.DATE_FORMAT,
            "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$",
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
        
        addRule(createRule(
            "Total Amount",
            "utility_bill",
            "total_amount",
            ValidationRule.RuleType.PRESENCE,
            null,
            null, null, null,
            true,
            ValidationRule.ValidationSeverity.HARDBLOCK,
            0.7
        ));
    }
    
    public List<ValidationRule> findAll() {
        return new ArrayList<>(rules.values());
    }
    
    public ValidationRule findById(String id) {
        return rules.get(id);
    }
    
    public List<ValidationRule> findByDocumentType(String documentType) {
        return rules.values().stream()
                .filter(rule -> rule.getDocumentType().equals(documentType))
                .collect(Collectors.toList());
    }
    
    public ValidationRule save(ValidationRule rule) {
        if (rule.getId() == null) {
            rule.setId(UUID.randomUUID().toString());
        }
        rules.put(rule.getId(), rule);
        return rule;
    }
    
    public void delete(String id) {
        rules.remove(id);
    }
    
    private void addRule(ValidationRule rule) {
        rules.put(rule.getId(), rule);
    }
    
    private ValidationRule createRule(
            String name, String documentType, String fieldName, ValidationRule.RuleType ruleType,
            String pattern, Double minValue, Double maxValue, List<String> allowedValues,
            boolean required, ValidationRule.ValidationSeverity severity, Double confidenceThreshold) {
        
        return ValidationRule.builder()
                .id(UUID.randomUUID().toString())
                .name(name)
                .description("Validation rule for " + fieldName + " in " + documentType)
                .documentType(documentType)
                .fieldName(fieldName)
                .ruleType(ruleType)
                .pattern(pattern)
                .minValue(minValue)
                .maxValue(maxValue)
                .allowedValues(allowedValues)
                .required(required)
                .severity(severity)
                .confidenceThreshold(confidenceThreshold)
                .build();
    }
}
