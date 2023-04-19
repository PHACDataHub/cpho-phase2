import { AttachmentIcon } from "@chakra-ui/icons";
import {
  Button,
  Center,
  Heading,
  Input,
  Spinner,
  VStack,
} from "@chakra-ui/react";
import { useState } from "react";
import { FileFormat } from "../../utils/types";
import { FileTypeChoice } from "./FileTypeChoice";

const FileUpload = ({
  fileToUpload,
  setFileToUpload,
  setStage,
  data,
  loading,
  error,
}: {
  fileToUpload: File | undefined;
  setFileToUpload: (file: File | undefined) => void;
  setStage: (stage: "upload" | "review_schema" | "review_data") => void;
  data: any;
  loading: boolean;
  error: any;
}) => {
  const [activeType, setActiveType] = useState<FileFormat>("indicator");

  const handleFile = (event: any) => {
    event.preventDefault();
    const file = event.target.files[0];
    setFileToUpload(file);
  };

  return (
    <VStack align="flex-start" spacing={4}>
      <FileTypeChoice activeType={activeType} setActiveType={setActiveType} />
      <Center
        cursor={
          data?.importData?.success || activeType !== "indicator"
            ? "default"
            : "pointer"
        }
        backgroundColor="gray.100"
        _dark={{ backgroundColor: "gray.600" }}
        w="100%"
        py={8}
        onClick={() => document.getElementById("file_input")?.click()}
      >
        <Input
          id="file_input"
          display="none"
          name="uploaded_file"
          accept="text/csv"
          type="file"
          onChange={handleFile}
          disabled={activeType !== "indicator"}
        />
        {loading ? (
          <Spinner />
        ) : (
          <VStack
            color={activeType === "indicator" ? "initial" : "gray.400"}
            _dark={
              activeType === "indicator"
                ? { color: "white" }
                : { color: "gray.500" }
            }
          >
            {!data?.importData?.success && <AttachmentIcon boxSize="8" />}
            <Heading size="lg" fontWeight={600}>
              {data?.importData?.success
                ? `Successfully uploaded ${(fileToUpload as any).name}`
                : error
                ? `Could not upload ${(fileToUpload as any).name}`
                : fileToUpload
                ? (fileToUpload as any).name
                : activeType === "indicator"
                ? "Click to select a file"
                : `Import not available for ${
                    activeType === "benchmarking"
                      ? "Benchmarking"
                      : "Trend Analysis"
                  } yet`}
            </Heading>
          </VStack>
        )}
      </Center>

      <VStack w="100%" align="flex-end">
        <Button
          size="lg"
          fontSize={20}
          colorScheme="blue"
          onClick={() => setStage("review_schema")}
          isDisabled={!fileToUpload}
        >
          Review
        </Button>
      </VStack>
    </VStack>
  );
};

export default FileUpload;
