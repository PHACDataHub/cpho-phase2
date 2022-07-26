import { Box, Heading, useDisclosure } from "@chakra-ui/react";
import { useSmallScreen } from "../../utils/hooks";
import { DataPoint } from "../../utils/types";
import { AddDataPointModal } from "./AddDataPointModal";

function DataPointCard({
  dataPoint,
  dataPoints,
  setDataPoints,
}: {
  dataPoint: DataPoint;
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <>
      <Box
        boxShadow="md"
        borderRadius="md"
        flexGrow={1}
        onClick={onOpen}
        cursor="pointer"
        transition="all 0.2s ease-in-out"
        _hover={{
          boxShadow: "xl",
        }}
      >
        <Box h="8px" w="100%" bgColor="pink.400" borderTopRadius="md" />
        <Box p={4}>
          <Heading size="md">
            {dataPoint.single_year_timeframe ?? dataPoint.multi_year_timeframe}
          </Heading>
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
          dataPoint={dataPoint}
          dataPoints={dataPoints}
          setDataPoints={setDataPoints}
        />
      ))}
    </Box>
  );
}
