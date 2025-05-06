package com.ocr.splitting.controller;

import com.ocr.splitting.model.SplitRequest;
import com.ocr.splitting.model.SplitResult;
import com.ocr.splitting.service.DocumentSplittingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/splitting")
@RequiredArgsConstructor
@Slf4j
public class DocumentSplittingController {

    private final DocumentSplittingService splittingService;

    @PostMapping
    public ResponseEntity<SplitResult> splitDocument(@Valid @RequestBody SplitRequest request) {
        log.info("Received split request for document: {}", request.getDocumentId());
        SplitResult result = splittingService.splitDocument(request);
        log.info("Split result for document {}: success={}, documents={}", 
                request.getDocumentId(), result.isSuccess(), 
                result.getDocuments() != null ? result.getDocuments().size() : 0);
        return ResponseEntity.ok(result);
    }
}
