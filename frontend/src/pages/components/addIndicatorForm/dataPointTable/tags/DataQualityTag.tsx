import { Box, Heading, Icon } from "@chakra-ui/react";
import { AiOutlineWarning } from "react-icons/ai";
import { BsStar, BsStarFill } from "react-icons/bs";
import { FaRegThumbsUp } from "react-icons/fa";
import { DataQualityType } from "../../../../../utils/types";

const DataQualityTag = ({ dataQuality }: { dataQuality: DataQualityType }) => {
  const [label, color, icon] = (() => {
    switch (dataQuality) {
      case "CAUTION":
        return ["Caution", "red.100", AiOutlineWarning];
      case "ACCEPTABLE":
        return ["Acceptable", "blue.100", FaRegThumbsUp];
      case "GOOD":
        return ["Good", "green.100", BsStar];
      case "EXCELLENT":
        return ["Excellent", "orange.100", BsStarFill];
      default:
        return ["Not Selected", "gray.100", undefined];
    }
  })();
  return (
    <Box bgColor={color} p={2} borderRadius="md" display="inline-block">
      <Heading size="xs">
        <Icon as={icon} mr={1} />
        {label}
      </Heading>
    </Box>
  );
};

export default DataQualityTag;
