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
import { ProvincesTerritories, Regions } from "../../../utils/constants";
import { GeographyType, LocationType } from "../../../utils/types";

const LocationTag = ({
  location,
  setLocation,
  geographyType,
}: {
  location: LocationType;
  setLocation: (location: LocationType) => void;
  geographyType: GeographyType;
}) => {
  const [label, color] = (() => {
    switch (location) {
      case "AB":
        return ["Alberta", "blue.100"];
      case "BC":
        return ["British Columbia", "blue.100"];
      case "MB":
        return ["Manitoba", "blue.100"];
      case "NB":
        return ["New Brunswick", "blue.100"];
      case "NL":
        return ["Newfoundland and Labrador", "blue.100"];
      case "NS":
        return ["Nova Scotia", "blue.100"];
      case "NT":
        return ["Northwest Territories", "blue.100"];
      case "NU":
        return ["Nunavut", "blue.100"];
      case "ON":
        return ["Ontario", "blue.100"];
      case "PE":
        return ["Prince Edward Island", "blue.100"];
      case "QC":
        return ["Quebec", "blue.100"];
      case "SK":
        return ["Saskatchewan", "blue.100"];
      case "YT":
        return ["Yukon", "blue.100"];
      case "CANADA":
        return ["Canada", "red.100"];
      case "ATLANTIC":
        return ["Atlantic", "green.100"];
      case "PRAIRIE":
        return ["Prairie", "green.100"];
      case "TERRITORIES":
        return ["Territories", "green.100"];
      default:
        return ["Not Selected", "orange.100"];
    }
  })();

  return (
    <Popover placement="right" trigger="hover">
      <PopoverTrigger>
        <Box
          bgColor={color}
          p={2}
          borderRadius="md"
          display="inline-block"
          cursor={location !== "CANADA" ? "pointer" : "default"}
          transition="all 0.2s ease-in-out"
          _hover={{ transform: location !== "CANADA" && "scale(1.075)" }}
        >
          <Heading size="xs">{label}</Heading>
        </Box>
      </PopoverTrigger>
      <PopoverContent w="100%">
        <PopoverArrow bgColor="gray.100" />
        <VStack align="stretch" spacing={0} shadow="lg">
          {geographyType === "PROVINCE_TERRITORY" &&
            ProvincesTerritories.map((option, idx) => (
              <Button
                borderRadius={0}
                borderTopRadius={idx === 0 ? "md" : 0}
                borderBottomRadius={
                  idx === ProvincesTerritories.length - 1 ? "md" : 0
                }
                key={option.value}
                size="sm"
                isActive={location === option.value}
                onClick={() => setLocation(option.value as LocationType)}
              >
                {option.label}
              </Button>
            ))}
          {geographyType === "REGION" &&
            Regions.map((option, idx) => (
              <Button
                borderRadius={0}
                borderTopRadius={idx === 0 ? "md" : 0}
                borderBottomRadius={idx === Regions.length - 1 ? "md" : 0}
                key={option.value}
                size="sm"
                isActive={location === option.value}
                onClick={() => setLocation(option.value as LocationType)}
              >
                {option.label}
              </Button>
            ))}
        </VStack>
      </PopoverContent>
    </Popover>
  );
};

export default LocationTag;
