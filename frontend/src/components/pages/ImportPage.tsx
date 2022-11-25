import { AttachmentIcon } from "@chakra-ui/icons";
import {
  VStack,
  Input,
  Button,
  Heading,
  Center,
  Spinner,
} from "@chakra-ui/react";
import { useState } from "react";
import { FileFormat } from "../../utils/types";
import { FileTypeChoice } from "../organisms/FileTypeChoice";
import { Page } from "../template/Page";

export function ImportPage() {
  const [fileToUpload, setFileToUpload] = useState();
  const [status, setStatus] = useState<
    "idle" | "loading" | "failure" | "success"
  >("idle");

  const [activeType, setActiveType] = useState<FileFormat>("indicator");

  const handleFile = (event: any) => {
    event.preventDefault();
    const file = event.target.files[0];
    setFileToUpload(file);
    setStatus("idle");
    console.log("GOT IT!", file);
  };

  const handleSubmit = (event: any) => {
    event.preventDefault();
    let formData = new FormData();
    if (fileToUpload) {
      setStatus("loading");
      formData.append("file", fileToUpload);
      console.log("Submit");
      if (fileToUpload) {
        fetch(
          (process.env.REACT_APP_SERVER_URL || "http://localhost:8000/") +
            "api/import",
          {
            method: "POST",
            body: formData,
          }
        )
          .then((res) => {
            if (res.status === 200) {
              setStatus("success");
            } else {
              setStatus("failure");
            }
            console.log(res);
          })
          .catch((err) => {
            setStatus("failure");
            console.log(err);
          });
      }
    }
  };

  return (
    <Page title="Import File" backButton={{ show: true, redirectUrl: "/" }}>
      <Heading size="md" fontWeight={500} mb={4}>
        The format of the file must align with the order and presence of the
        expected columns
      </Heading>
      <VStack align="flex-start" spacing={4}>
        <FileTypeChoice activeType={activeType} setActiveType={setActiveType} />
        <Center
          cursor={
            status === "success" || activeType !== "indicator"
              ? "default"
              : "pointer"
          }
          backgroundColor="gray.100"
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
          {status === "loading" ? (
            <Spinner />
          ) : (
            <VStack color={activeType === "indicator" ? "initial" : "gray.400"}>
              {status !== "success" && <AttachmentIcon boxSize="8" />}
              <Heading size="lg" fontWeight={600}>
                {status === "success"
                  ? `Successfully uploaded ${(fileToUpload as any).name}`
                  : status === "failure"
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
            colorScheme="red"
            onClick={handleSubmit}
          >
            Import
          </Button>
        </VStack>
      </VStack>
    </Page>
  );
}
