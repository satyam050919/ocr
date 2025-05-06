package com.ocr.splitting.service;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;
import java.util.Map;

@FeignClient(name = "document-classification-service", url = "${feign.client.document-classification.url}")
public interface DocumentClassificationClient {

    @PostMapping("/api/v1/classify")
    ClassificationResponse classifyDocument(@RequestBody ClassificationRequest request);
    
    class ClassificationRequest {
        private String documentId;
        private String documentPath;
        
        public String getDocumentId() {
            return documentId;
        }
        
        public void setDocumentId(String documentId) {
            this.documentId = documentId;
        }
        
        public String getDocumentPath() {
            return documentPath;
        }
        
        public void setDocumentPath(String documentPath) {
            this.documentPath = documentPath;
        }
    }
    
    class ClassificationResponse {
        private String documentId;
        private List<DocumentType> documentTypes;
        
        public String getDocumentId() {
            return documentId;
        }
        
        public void setDocumentId(String documentId) {
            this.documentId = documentId;
        }
        
        public List<DocumentType> getDocumentTypes() {
            return documentTypes;
        }
        
        public void setDocumentTypes(List<DocumentType> documentTypes) {
            this.documentTypes = documentTypes;
        }
    }
    
    class DocumentType {
        private String type;
        private double confidence;
        private Map<String, Integer> pageNumbers;
        
        public String getType() {
            return type;
        }
        
        public void setType(String type) {
            this.type = type;
        }
        
        public double getConfidence() {
            return confidence;
        }
        
        public void setConfidence(double confidence) {
            this.confidence = confidence;
        }
        
        public Map<String, Integer> getPageNumbers() {
            return pageNumbers;
        }
        
        public void setPageNumbers(Map<String, Integer> pageNumbers) {
            this.pageNumbers = pageNumbers;
        }
    }
}
