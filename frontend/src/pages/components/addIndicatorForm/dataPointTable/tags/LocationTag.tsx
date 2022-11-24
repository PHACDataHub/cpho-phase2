import { Box, Heading } from "@chakra-ui/react";
import { LocationType } from "../../../../../utils/types";

const LocationTag = ({ location }: { location: LocationType }) => {
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
    <Box bgColor={color} p={2} borderRadius="md" display="inline-block">
      <Heading size="xs">{label}</Heading>
    </Box>
  );
};

export default LocationTag;
