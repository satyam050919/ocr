package com.ocr.splitting.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SplitResult {
    private String originalDocumentId;
    private List<SplitDocument> documents;
    private boolean success;
    private String errorMessage;
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SplitDocument {
        private String id;
        private String name;
        private String type;
        private int pageCount;
        private double confidence;
        private String filePath;
        private String previewUrl;
        private String size;
    }
}
