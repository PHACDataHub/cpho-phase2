import { Box, Heading } from "@chakra-ui/react";

const ValueTag = ({ value }: { value: number }) => {
  return (
    <Box bgColor="gray.200" p={2} borderRadius="md" display="inline-block">
      <Heading size="xs">{value}</Heading>
    </Box>
  );
};

export default ValueTag;
