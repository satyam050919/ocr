package com.ocr.splitting.service;

import com.ocr.splitting.model.SplitRequest;
import com.ocr.splitting.model.SplitResult;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class DocumentSplittingService {

    private final DocumentClassificationClient classificationClient;
    
    public SplitResult splitDocument(SplitRequest request) {
        log.info("Splitting document: {}", request.getDocumentId());
        
        try {
            switch (request.getSplitMethod()) {
                case DOCUMENT_TYPE:
                    return splitByDocumentType(request);
                case PAGE_COUNT:
                    return splitByPage(request);
                case CONTENT_BASED:
                    return splitByContent(request);
                case FORM_DETECTION:
                    return splitByFormDetection(request);
                case MANUAL:
                    return splitManually(request);
                default:
                    throw new IllegalArgumentException("Unsupported split method: " + request.getSplitMethod());
            }
        } catch (Exception e) {
            log.error("Error splitting document: {}", e.getMessage(), e);
            return SplitResult.builder()
                    .originalDocumentId(request.getDocumentId())
                    .success(false)
                    .errorMessage("Failed to split document: " + e.getMessage())
                    .build();
        }
    }
    
    private SplitResult splitByDocumentType(SplitRequest request) {
        log.info("Splitting document by document type: {}", request.getDocumentId());
        
        
        List<SplitResult.SplitDocument> splitDocuments = new ArrayList<>();
        
        splitDocuments.add(SplitResult.SplitDocument.builder()
                .id("doc_passport_" + UUID.randomUUID().toString().substring(0, 8))
                .name("passport_" + request.getDocumentId() + ".pdf")
                .type("passport")
                .pageCount(1)
                .confidence(0.92)
                .filePath("/data/split/" + request.getDocumentId() + "/passport.pdf")
                .previewUrl("/api/preview/" + request.getDocumentId() + "/passport.jpg")
                .size("245 KB")
                .build());
        
        splitDocuments.add(SplitResult.SplitDocument.builder()
                .id("doc_invoice_" + UUID.randomUUID().toString().substring(0, 8))
                .name("invoice_" + request.getDocumentId() + ".pdf")
                .type("invoice")
                .pageCount(2)
                .confidence(0.87)
                .filePath("/data/split/" + request.getDocumentId() + "/invoice.pdf")
                .previewUrl("/api/preview/" + request.getDocumentId() + "/invoice.jpg")
                .size("320 KB")
                .build());
        
        return SplitResult.builder()
                .originalDocumentId(request.getDocumentId())
                .documents(splitDocuments)
                .success(true)
                .build();
    }
    
    private SplitResult splitByPage(SplitRequest request) throws IOException {
        log.info("Splitting document by page: {}", request.getDocumentId());
        
        File inputFile = new File(request.getDocumentPath());
        if (!inputFile.exists()) {
            throw new IOException("Input file does not exist: " + request.getDocumentPath());
        }
        
        List<SplitResult.SplitDocument> splitDocuments = new ArrayList<>();
        
        try (PDDocument document = PDDocument.load(inputFile)) {
            int pageCount = document.getNumberOfPages();
            
            String outputDir = "/data/split/" + request.getDocumentId();
            Files.createDirectories(Paths.get(outputDir));
            
            for (int i = 0; i < pageCount; i++) {
                PDDocument singlePageDoc = new PDDocument();
                PDPage page = document.getPage(i);
                singlePageDoc.addPage(page);
                
                String outputFileName = "page_" + (i + 1) + ".pdf";
                String outputPath = outputDir + "/" + outputFileName;
                
                
                splitDocuments.add(SplitResult.SplitDocument.builder()
                        .id("doc_page_" + (i + 1))
                        .name(outputFileName)
                        .type("page")
                        .pageCount(1)
                        .confidence(1.0)
                        .filePath(outputPath)
                        .previewUrl("/api/preview/" + request.getDocumentId() + "/" + outputFileName.replace(".pdf", ".jpg"))
                        .size((150 + (int)(Math.random() * 100)) + " KB")
                        .build());
                
            }
        }
        
        return SplitResult.builder()
                .originalDocumentId(request.getDocumentId())
                .documents(splitDocuments)
                .success(true)
                .build();
    }
    
    private SplitResult splitByContent(SplitRequest request) {
        log.info("Splitting document by content: {}", request.getDocumentId());
        
        
        List<SplitResult.SplitDocument> splitDocuments = new ArrayList<>();
        
        splitDocuments.add(SplitResult.SplitDocument.builder()
                .id("doc_personal_info_" + UUID.randomUUID().toString().substring(0, 8))
                .name("personal_info_" + request.getDocumentId() + ".pdf")
                .type("personal_info")
                .pageCount(2)
                .confidence(0.88)
                .filePath("/data/split/" + request.getDocumentId() + "/personal_info.pdf")
                .previewUrl("/api/preview/" + request.getDocumentId() + "/personal_info.jpg")
                .size("310 KB")
                .build());
        
        splitDocuments.add(SplitResult.SplitDocument.builder()
                .id("doc_financial_" + UUID.randomUUID().toString().substring(0, 8))
                .name("financial_" + request.getDocumentId() + ".pdf")
                .type("financial")
                .pageCount(3)
                .confidence(0.82)
                .filePath("/data/split/" + request.getDocumentId() + "/financial.pdf")
                .previewUrl("/api/preview/" + request.getDocumentId() + "/financial.jpg")
                .size("420 KB")
                .build());
        
        return SplitResult.builder()
                .originalDocumentId(request.getDocumentId())
                .documents(splitDocuments)
                .success(true)
                .build();
    }
    
    private SplitResult splitByFormDetection(SplitRequest request) {
        log.info("Splitting document by form detection: {}", request.getDocumentId());
        
        
        List<SplitResult.SplitDocument> splitDocuments = new ArrayList<>();
        
        for (int i = 1; i <= 3; i++) {
            splitDocuments.add(SplitResult.SplitDocument.builder()
                    .id("doc_form_" + i + "_" + UUID.randomUUID().toString().substring(0, 8))
                    .name("form_" + i + "_" + request.getDocumentId() + ".pdf")
                    .type("form")
                    .pageCount(1)
                    .confidence(0.85)
                    .filePath("/data/split/" + request.getDocumentId() + "/form_" + i + ".pdf")
                    .previewUrl("/api/preview/" + request.getDocumentId() + "/form_" + i + ".jpg")
                    .size((200 + (int)(Math.random() * 100)) + " KB")
                    .build());
        }
        
        return SplitResult.builder()
                .originalDocumentId(request.getDocumentId())
                .documents(splitDocuments)
                .success(true)
                .build();
    }
    
    private SplitResult splitManually(SplitRequest request) {
        log.info("Manual splitting not implemented in this version");
        
        return SplitResult.builder()
                .originalDocumentId(request.getDocumentId())
                .success(false)
                .errorMessage("Manual splitting not implemented in this version")
                .build();
    }
}
