from rag_pipeline import ingest_document_chunks

SAMPLE_KNOWLEDGE_BASE = [
    {
        "id": "chunk_1",
        "text": "LM7805 Linear Regulator Datasheet: Absolute maximum input voltage is 35V DC. Operating output voltage is 4.75V to 5.25V with 5.0V typical. Maximum output current without external pass transistor is 1.5A when adequate heat sinking is provided.",
        "metadata": {"source": "LM7805_Datasheet.pdf", "section": "Absolute Maximum Ratings"}
    },
    {
        "id": "chunk_2",
        "text": "LM7805 Thermal Specifications: Junction-to-case thermal resistance (R_theta_JC) is 5 C/W for TO-220 package. Maximum operating junction temperature is 125 C. Dropout voltage is typically 2.0V at 1A load current.",
        "metadata": {"source": "LM7805_Datasheet.pdf", "section": "Thermal Characteristics"}
    },
    {
        "id": "chunk_3",
        "text": "ESP32 Pinout & Power Guidelines: Recommended operating input voltage on VDD3P3 pins is 3.0V to 3.6V. Peak current during RF transmission can reach 500mA; power rails require a minimum of 10uF ceramic decoupling capacitor placed close to chip.",
        "metadata": {"source": "ESP32_Hardware_Design_Guide.pdf", "section": "Power Supply"}
    }
]

if __name__ == "__main__":
    print("Seeding local ChromaDB vector store...")
    ingest_document_chunks(SAMPLE_KNOWLEDGE_BASE)