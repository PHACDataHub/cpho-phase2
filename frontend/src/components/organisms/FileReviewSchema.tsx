import {
  VStack,
  Heading,
  HStack,
  FormControl,
  FormLabel,
  Select,
  Button,
  Text,
} from "@chakra-ui/react";
import { FileColumnData } from "../../utils/constants";

const FileReviewSchema = ({
  fieldMapping,
  setFieldMapping,
  setStage,
  fileHeaders,
}: {
  fieldMapping: { [key: string]: string };
  setFieldMapping: (mapping: { [key: string]: string }) => void;
  setStage: (stage: "upload" | "review_schema" | "review_data") => void;
  fileHeaders: string[];
}) => {
  return (
    <VStack align="flex-start" spacing={4}>
      <Heading size="lg" fontWeight={600}>
        Review Schema
      </Heading>
      <Text>
        Please review the schema below and make sure it matches the file you
        uploaded. If it does not, please go back and upload the correct file.
      </Text>
      <VStack w="100%" align="flex-start" spacing={4}>
        <Heading size="md" fontWeight={600}>
          File Headers
        </Heading>
        <Text>
          Please select the corresponding field for each header. If the header
          is not in the list, please select "Custom Field" and enter the name of
          the field in the input box.
        </Text>
        <VStack w="100%" spacing={4}>
          {FileColumnData.indicator.map((header) => (
            <HStack
              key={header.value}
              w={["100%", "100%", "50%"]}
              spacing={4}
              justify="space-between"
            >
              {/* <Text textAlign="right">
              {header.label}{" "}
              {header.required && (
                <Text as="span" color="red">
                  *
                </Text>
              )}
            </Text> */}

              <FormControl
                isRequired={header.required}
                isInvalid={header.required && fieldMapping[header.value] === ""}
                display="flex"
                flexDir="row"
                alignItems="center"
                w="100%"
                justifyContent="space-between"
              >
                <FormLabel>{header.label}</FormLabel>
                <Select
                  w="50%"
                  placeholder="Select Field"
                  value={fieldMapping[header.value]}
                  onChange={(e) =>
                    setFieldMapping({
                      ...fieldMapping,
                      [header.value]: e.target.value,
                    })
                  }
                >
                  {fileHeaders.map((fileHeader) => (
                    <option key={fileHeader} value={fileHeader}>
                      {fileHeader}
                    </option>
                  ))}
                </Select>
              </FormControl>
            </HStack>
          ))}
        </VStack>
      </VStack>
      <VStack w="100%" align="flex-end">
        <Button
          size="lg"
          fontSize={20}
          colorScheme="blue"
          onClick={() => setStage("upload")}
        >
          Back
        </Button>
        <Button
          size="lg"
          fontSize={20}
          colorScheme="blue"
          onClick={() => setStage("review_data")}
        >
          Review Data
        </Button>
      </VStack>
    </VStack>
  );
};

export default FileReviewSchema;
