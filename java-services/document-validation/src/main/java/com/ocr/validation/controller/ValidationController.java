package com.ocr.validation.controller;

import com.ocr.validation.model.ValidationRequest;
import com.ocr.validation.model.ValidationResult;
import com.ocr.validation.service.ValidationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/validation")
@RequiredArgsConstructor
@Slf4j
public class ValidationController {

    private final ValidationService validationService;

    @PostMapping
    public ResponseEntity<ValidationResult> validateDocument(@Valid @RequestBody ValidationRequest request) {
        log.info("Received validation request for document: {}", request.getDocumentId());
        ValidationResult result = validationService.validateDocument(request);
        log.info("Validation result for document {}: valid={}, issues={}", 
                request.getDocumentId(), result.isValid(), result.getIssues().size());
        return ResponseEntity.ok(result);
    }
}
