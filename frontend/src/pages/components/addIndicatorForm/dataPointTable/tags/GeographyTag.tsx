import {
  Box,
  Button,
  ButtonGroup,
  Heading,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
} from "@chakra-ui/react";

const GeographyTag = ({
  type,
  setGeography,
}: {
  type: "COUNTRY" | "REGION" | "PROVINCE_TERRITORY";
  setGeography: (geography: string) => void;
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
    <Popover placement="top">
      <PopoverTrigger>
        <Box
          bgColor={tagColor}
          p={2}
          borderRadius="md"
          display="inline-block"
          cursor="pointer"
          transition="all 0.2s ease-in-out"
          _hover={{
            transform: "scale(1.075)",
          }}
        >
          <Heading size="xs">{tagText}</Heading>
        </Box>
      </PopoverTrigger>
      <PopoverContent w="100%">
        <PopoverArrow />
        <ButtonGroup isAttached p={2}>
          <Button
            isActive={type === "COUNTRY"}
            size="sm"
            onClick={() => setGeography("COUNTRY")}
          >
            Country
          </Button>
          <Button
            isActive={type === "REGION"}
            size="sm"
            onClick={() => setGeography("REGION")}
          >
            Region
          </Button>
          <Button
            isActive={type === "PROVINCE_TERRITORY"}
            size="sm"
            onClick={() => setGeography("PROVINCE_TERRITORY")}
          >
            Province/Territory
          </Button>
        </ButtonGroup>
      </PopoverContent>
    </Popover>
  );
};

export default GeographyTag;
