import { CopyIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Box,
  Heading,
  HStack,
  Icon,
  IconButton,
  Tag,
  useDisclosure,
} from "@chakra-ui/react";
import { getCleanPTName, useSmallScreen } from "../../utils/hooks";
import { DataPoint } from "../../utils/types";
import { AddDataPointModal } from "./AddDataPointModal";
import { BsFillPersonFill } from "react-icons/bs";
import { FaGenderless } from "react-icons/fa";
import { AiOutlineNumber } from "react-icons/ai";

function DataPointCard({
  index,
  dataPoint,
  dataPoints,
  setDataPoints,
}: {
  index: number;
  dataPoint: DataPoint;
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const onDelete = () => {
    const idx = dataPoints.indexOf(dataPoint);
    if (idx === -1) return;
    setDataPoints(dataPoints.slice(0, idx).concat(dataPoints.slice(idx + 1)));
  };

  const onDuplicate = () => {
    const idx = dataPoints.indexOf(dataPoint);
    if (idx === -1) return;
    setDataPoints([...dataPoints, dataPoints[idx]]);
  };
  return (
    <>
      <Box
        position="relative"
        boxShadow="md"
        borderRadius="md"
        maxW="200px"
        flexGrow={1}
        transition="all 0.2s ease-in-out"
        _hover={{
          boxShadow: "2xl",
        }}
      >
        <Box
          h="8px"
          w="100%"
          bgColor={`brand.${index + 1}`}
          borderTopRadius="md"
        />
        <Box p={2} pl={3}>
          <HStack justify="flex-end" spacing={1}>
            <IconButton
              onClick={onDelete}
              colorScheme="red"
              isRound
              icon={<DeleteIcon />}
              aria-label={"Delete data point"}
              size="sm"
            />
            <IconButton
              onClick={onOpen}
              colorScheme="blue"
              isRound
              icon={<EditIcon />}
              aria-label={"Delete data point"}
              size="sm"
            />
            <IconButton
              onClick={onDuplicate}
              colorScheme="green"
              isRound
              icon={<CopyIcon />}
              aria-label={"Duplicate data point"}
              size="sm"
            />
          </HStack>
          <Heading size="sm">
            {dataPoint.single_year_timeframe ?? dataPoint.multi_year_timeframe}
          </Heading>
          <Heading size="xs">{getCleanPTName(dataPoint.country)}</Heading>
          <Box pt={2} display="flex" flexWrap="wrap" gap={1}>
            {dataPoint.age_group && (
              <Tag size="sm" colorScheme="blue">
                <Icon as={BsFillPersonFill} />
                {dataPoint.age_group}
              </Tag>
            )}
            {dataPoint.sex && (
              <Tag size="sm" colorScheme="red">
                <Icon as={FaGenderless} />
                {dataPoint.sex}
              </Tag>
            )}
            {dataPoint.value && (
              <Tag size="sm" colorScheme="green">
                <Icon as={AiOutlineNumber} /> {dataPoint.value}
              </Tag>
            )}
          </Box>
        </Box>
      </Box>
      <AddDataPointModal
        isOpen={isOpen}
        onClose={onClose}
        dataPoints={dataPoints}
        dataPointIdx={dataPoints.indexOf(dataPoint)}
        setDataPoints={setDataPoints}
      />
    </>
  );
}

export function DataPointContainer({
  dataPoints,
  setDataPoints,
}: {
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  const isSmallScreen = useSmallScreen();
  return (
    <Box
      display="flex"
      flexWrap="wrap"
      justifyContent={isSmallScreen ? "center" : ""}
      // alignItems="flex-start"
      alignContent={isSmallScreen ? "" : "flex-start"}
      gap={4}
      maxW="90%"
      p={1}
    >
      {dataPoints.map((dataPoint, idx) => (
        <DataPointCard
          key={idx}
          index={idx}
          dataPoint={dataPoint}
          dataPoints={dataPoints}
          setDataPoints={setDataPoints}
        />
      ))}
    </Box>
  );
}
