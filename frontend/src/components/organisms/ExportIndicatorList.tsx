import {
  VStack,
  Heading,
  Input,
  HStack,
  IconButton,
  Icon,
  Popover,
  PopoverTrigger,
  PopoverContent,
  Button,
} from "@chakra-ui/react";
import { useState } from "react";
import { PossibleIndicatorType } from "../../utils/types";
import PossibleIndicatorBox from "../molecules/PossibleIndicatorBox";
import {
  FaSortAlphaDown,
  FaSortAlphaDownAlt,
  FaSortNumericDown,
  FaSortNumericDownAlt,
} from "react-icons/fa";

const ExportIndicatorList = ({
  indicators,
  addSelected,
  removeSelected,
  toggleSelected,
}: {
  indicators: PossibleIndicatorType[];
  addSelected: (ind: PossibleIndicatorType) => void;
  removeSelected: (ind: PossibleIndicatorType) => void;
  toggleSelected: (ind: PossibleIndicatorType) => void;
}) => {
  const [search, setSearch] = useState("");

  const [sortOption, setSortOption] = useState<"name" | "dataPointCount">(
    "name"
  );
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const regex = new RegExp(search.trim(), "i");

  const filteredIndicators = indicators
    .filter((ind) => regex.test(ind.name))
    .sort((a, b) => {
      if (sortOption === "name") {
        if (sortDir === "asc") {
          return a.name.localeCompare(b.name);
        } else {
          return b.name.localeCompare(a.name);
        }
      } else {
        if (sortDir === "asc") {
          return a.dataPointCount - b.dataPointCount;
        } else {
          return b.dataPointCount - a.dataPointCount;
        }
      }
    });

  return (
    <VStack w={["100%", "100%", "60%"]}>
      <Heading alignSelf="start" size="md">
        Select Indicators to Export
      </Heading>
      <HStack w="100%">
        <Input
          placeholder="Search for an indicator"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Popover>
          <PopoverTrigger>
            <IconButton
              aria-label="Toggle filter options"
              icon={
                <Icon
                  as={
                    sortOption === "name"
                      ? sortDir === "asc"
                        ? FaSortAlphaDown
                        : FaSortAlphaDownAlt
                      : sortDir === "asc"
                      ? FaSortNumericDown
                      : FaSortNumericDownAlt
                  }
                />
              }
            />
          </PopoverTrigger>
          <PopoverContent margin={0}>
            <VStack spacing={0} align="stretch" margin={0}>
              <Button
                margin={0}
                isActive={sortOption === "name" && sortDir === "asc"}
                borderRadius={0}
                onClick={() => {
                  setSortOption("name");
                  setSortDir("asc");
                }}
                leftIcon={<Icon as={FaSortAlphaDown} />}
              >
                Sort by name (A-Z)
              </Button>
              <Button
                margin={0}
                isActive={sortOption === "name" && sortDir === "desc"}
                borderRadius={0}
                onClick={() => {
                  setSortOption("name");
                  setSortDir("desc");
                }}
                leftIcon={<Icon as={FaSortAlphaDownAlt} />}
              >
                Sort by name (Z-A)
              </Button>
              <Button
                margin={0}
                isActive={sortOption === "dataPointCount" && sortDir === "asc"}
                borderRadius={0}
                onClick={() => {
                  setSortOption("dataPointCount");
                  setSortDir("asc");
                }}
                leftIcon={<Icon as={FaSortNumericDown} />}
              >
                Lowest data point count
              </Button>
              <Button
                margin={0}
                isActive={sortOption === "dataPointCount" && sortDir === "desc"}
                borderRadius={0}
                onClick={() => {
                  setSortOption("dataPointCount");
                  setSortDir("desc");
                }}
                leftIcon={<Icon as={FaSortNumericDownAlt} />}
              >
                Highest data point count
              </Button>
            </VStack>
          </PopoverContent>
        </Popover>
      </HStack>
      <VStack overflow="scroll" maxH="50vh" align="stretch" w="100%">
        {indicators.length > 0 ? (
          filteredIndicators.map(
            (ind) =>
              ind.name.match(regex) && (
                <PossibleIndicatorBox
                  addSelected={addSelected}
                  removeSelected={removeSelected}
                  key={ind.id}
                  indicator={ind}
                  selected={false}
                  toggleSelect={() => toggleSelected(ind)}
                />
              )
          )
        ) : (
          <Heading size="lg" mx="auto">
            No data found in database
          </Heading>
        )}
      </VStack>
    </VStack>
  );
};

export default ExportIndicatorList;
