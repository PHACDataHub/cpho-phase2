import { Box, Heading } from "@chakra-ui/react";

const GeographyTag = ({
  type,
}: {
  type: "COUNTRY" | "REGION" | "PROVINCE_TERRITORY";
}) => {
  const getTagText = () => {
    switch (type) {
      case "COUNTRY":
        return "Country";
      case "REGION":
        return "Region";
      case "PROVINCE_TERRITORY":
        return "Province/Territory";
    }
  };

  const getTagColor = () => {
    switch (type) {
      case "COUNTRY":
        return "red.100";
      case "REGION":
        return "green.100";
      case "PROVINCE_TERRITORY":
        return "blue.100";
    }
  };

  const [tagText, tagColor] = [getTagText(), getTagColor()];

  return (
    <Box bgColor={tagColor} p={2} borderRadius="md" display="inline-block">
      <Heading size="xs">{tagText}</Heading>
    </Box>
  );
};

export default GeographyTag;
