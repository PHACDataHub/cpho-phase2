import {
  Box,
  Button,
  Heading,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
  VStack,
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
    <Popover placement="right" trigger="hover">
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
        <VStack spacing={0} align="stretch">
          {["Country", "Region", "Province/Territory"].map((option, idx) => (
            <Button
              borderRadius={0}
              borderTopRadius={idx === 0 ? "md" : 0}
              borderBottomRadius={idx === 2 ? "md" : 0}
              key={option}
              size="sm"
              isActive={type === option.replace("/", "_").toUpperCase()}
              onClick={() =>
                setGeography(option.replace("/", "_").toUpperCase())
              }
              _dark={{
                color: "white",
                bgColor: "gray.800",
                _hover: {
                  bgColor: "gray.700",
                },
                _active: {
                  bgColor: "gray.600",
                },
              }}
            >
              {option}
            </Button>
          ))}
        </VStack>
      </PopoverContent>
    </Popover>
  );
};

export default GeographyTag;
