import {
  VStack,
  Heading,
  HStack,
  FormControl,
  FormLabel,
  Select,
  Button,
  Text,
  Spacer,
} from "@chakra-ui/react";
import { FileColumnData } from "../../utils/constants";

const FileReviewSchema = ({
  fieldMapping,
  setFieldMapping,
  setStage,
  fileHeaders,
  validMapping,
}: {
  fieldMapping: { [key: string]: string };
  setFieldMapping: (mapping: { [key: string]: string }) => void;
  setStage: (stage: "upload" | "review_schema" | "review_data") => void;
  fileHeaders: string[];
  validMapping: boolean;
}) => {
  return (
    <VStack align="flex-start" spacing={4}>
      <HStack w="100%">
        <Button
          fontSize={20}
          colorScheme="blue"
          onClick={() => setStage("upload")}
        >
          Back
        </Button>
        <Spacer />
        <Button
          fontSize={20}
          colorScheme="blue"
          onClick={() => setStage("review_data")}
          isDisabled={!validMapping}
        >
          Review Data
        </Button>
      </HStack>
      <Heading size="lg" fontWeight={600}>
        Review Schema
      </Heading>
      <Text>
        Please review the schema below and match the fields to the correct
        columns in your file.
      </Text>

      <VStack w="100%" align="flex-start" spacing={4}>
        <VStack w="100%" spacing={4}>
          {FileColumnData.indicator.map((field) => (
            <HStack
              key={field.value}
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
                isRequired={field.required}
                isInvalid={field.required && fieldMapping[field.value] === ""}
                display="flex"
                flexDir="row"
                alignItems="center"
                w="100%"
                justifyContent="space-between"
              >
                <FormLabel>{field.label}</FormLabel>
                <Select
                  w="50%"
                  placeholder="Select Field"
                  value={fieldMapping[field.value]}
                  onChange={(e) =>
                    setFieldMapping({
                      ...fieldMapping,
                      [field.value]: e.target.value,
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
    </VStack>
  );
};

export default FileReviewSchema;
