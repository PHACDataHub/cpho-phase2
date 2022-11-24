import { Box, Heading, HStack } from "@chakra-ui/react";

const YearTag = ({ year }: { year: number | number[] }) => {
  if (Array.isArray(year)) {
    return (
      <HStack spacing={0.5}>
        <Box bgColor="gray.200" p={2} borderLeftRadius="md">
          <Heading size="xs">{year[0]}</Heading>
        </Box>
        <Box bgColor="gray.200" p={2} borderRightRadius="md">
          <Heading size="xs">{year[1]}</Heading>
        </Box>
      </HStack>
    );
  } else {
    return (
      <Box bgColor="gray.200" p={2} borderRadius="md" display="inline-block">
        <Heading size="xs">{year}</Heading>
      </Box>
    );
  }
};

export default YearTag;
