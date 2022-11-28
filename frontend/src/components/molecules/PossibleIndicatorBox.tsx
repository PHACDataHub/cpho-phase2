import { MinusIcon, AddIcon } from "@chakra-ui/icons";
import { HStack, IconButton, Heading } from "@chakra-ui/react";
import { useEffect } from "react";
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

  useEffect(() => {
    if (selected) {
      addSelected(indicator);
    } else {
      removeSelected(indicator);
    }
  }, [selected, indicator, addSelected, removeSelected]);

  return (
    <HStack
      p={4}
      borderRadius="md"
      bgColor={selected ? "gray.400" : "gray.200"}
      _hover={{ bgColor: selected ? "gray.400" : "gray.300" }}
      transition="all 0.2s ease-in-out"
    >
      <IconButton
        onClick={() => toggleSelect()}
        isRound
        size="sm"
        aria-label={`Add ${name} to export list`}
        icon={selected ? <MinusIcon /> : <AddIcon />}
      />
      <Heading size="sm">{name}</Heading>
      <Heading size="sm" fontWeight="normal" fontStyle="italic">
        {dataPointCount} data point{dataPointCount === 1 ? "" : "s"}
      </Heading>
    </HStack>
  );
};

export default PossibleIndicatorBox;
