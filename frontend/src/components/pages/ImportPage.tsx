import { useMutation } from "@apollo/client";
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
import { IMPORT_DATA } from "../../utils/graphql/mutations";
import { FileFormat } from "../../utils/types";
import { FileTypeChoice } from "../organisms/FileTypeChoice";
import { Page } from "../template/Page";

export function ImportPage() {
  const [fileToUpload, setFileToUpload] = useState();

  const [activeType, setActiveType] = useState<FileFormat>("indicator");
  const [importData, { loading, error, data }] = useMutation(IMPORT_DATA);

  const handleFile = (event: any) => {
    event.preventDefault();
    const file = event.target.files[0];
    setFileToUpload(file);
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault();
    if (fileToUpload) {
      try {
        await importData({
          variables: { file: fileToUpload },
        });
      } catch (error) {
        console.log(error);
      }
    }
  };

  console.log(data);

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
            data?.importData?.success || activeType !== "indicator"
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
          {loading ? (
            <Spinner />
          ) : (
            <VStack color={activeType === "indicator" ? "initial" : "gray.400"}>
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
