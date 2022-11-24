import { Box, Heading } from "@chakra-ui/react";

const UnitTag = ({ unit }: { unit: string }) => {
  const [label, color] = (() => {
    switch (unit) {
      case "PERCENT":
        return ["%", "green.100"];
      case "RATE":
        return ["Per 100k", "blue.100"];
      default:
        return [unit, "gray.100"];
    }
  })();
  return (
    <Box bgColor={color} p={2} borderRadius="md" display="inline-block">
      <Heading size="xs">{label}</Heading>
    </Box>
  );
};

export default UnitTag;
