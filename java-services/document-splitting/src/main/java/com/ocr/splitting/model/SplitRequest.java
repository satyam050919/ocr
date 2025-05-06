package com.ocr.splitting.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SplitRequest {
    private String documentId;
    private String documentPath;
    private SplitMethod splitMethod;
    private OutputFormat outputFormat;
    private String namingConvention;
    private Double minConfidence;
    private boolean preserveOriginal;
    
    public enum SplitMethod {
        DOCUMENT_TYPE,
        PAGE_COUNT,
        CONTENT_BASED,
        FORM_DETECTION,
        MANUAL
    }
    
    public enum OutputFormat {
        PDF,
        IMAGE,
        BOTH
    }
}
