package com.ocr.splitting;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class DocumentSplittingApplication {

    public static void main(String[] args) {
        SpringApplication.run(DocumentSplittingApplication.class, args);
    }
}
