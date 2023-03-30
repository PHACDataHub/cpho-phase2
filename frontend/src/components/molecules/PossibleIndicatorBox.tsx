import { MinusIcon, AddIcon } from "@chakra-ui/icons";
import { HStack, Heading, Icon, Spacer } from "@chakra-ui/react";
import { PossibleIndicatorType } from "../../utils/types";

const PossibleIndicatorBox = ({
  indicator,
  addSelected,
  removeSelected,
  selected,
  toggleSelect,
}: {
  indicator: PossibleIndicatorType;
  addSelected: (ind: PossibleIndicatorType) => void;
  removeSelected: (ind: PossibleIndicatorType) => void;
  selected: boolean;
  toggleSelect: () => void;
}) => {
  const { name, dataPointCount } = indicator;

  return (
    <HStack
      p={4}
      borderRadius="md"
      bgColor={selected ? "gray.400" : "gray.200"}
      _hover={{ bgColor: selected ? "gray.400" : "gray.300" }}
      _dark={{
        bgColor: selected ? "gray.500" : "gray.700",
        _hover: { bgColor: selected ? "gray.500" : "gray.600" },
      }}
      transition="all 0.2s ease-in-out"
      cursor="pointer"
      onClick={() => toggleSelect()}
    >
      <Heading size="sm">{name}</Heading>
      <Heading size="sm" fontWeight="normal" fontStyle="italic">
        {dataPointCount} data point{dataPointCount === 1 ? "" : "s"}
      </Heading>
      <Spacer />
      <Icon
        fontSize="sm"
        aria-label={`Add ${name} to export list`}
        as={selected ? MinusIcon : AddIcon}
      />
    </HStack>
  );
};

export default PossibleIndicatorBox;
