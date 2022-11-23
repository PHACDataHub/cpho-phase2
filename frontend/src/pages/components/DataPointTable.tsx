import {
  Heading,
  HStack,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { DataPoint } from "../../utils/types";

// function DataPointCard({
//   index,
//   dataPoint,
//   dataPoints,
//   setDataPoints,
// }: {
//   index: number;
//   dataPoint: DataPoint;
//   dataPoints: DataPoint[];
//   setDataPoints: (dataPoints: DataPoint[]) => void;
// }) {
//   const { isOpen, onOpen, onClose } = useDisclosure();

//   const onDelete = () => {
//     const idx = dataPoints.indexOf(dataPoint);
//     if (idx === -1) return;
//     setDataPoints(dataPoints.slice(0, idx).concat(dataPoints.slice(idx + 1)));
//   };

//   const onDuplicate = () => {
//     const idx = dataPoints.indexOf(dataPoint);
//     if (idx === -1) return;
//     setDataPoints([...dataPoints, dataPoints[idx]]);
//   };
//   return (
//     <>
//       <Box
//         position="relative"
//         boxShadow="md"
//         borderRadius="md"
//         maxW="200px"
//         flexGrow={1}
//         transition="all 0.2s ease-in-out"
//         _hover={{
//           boxShadow: "2xl",
//         }}
//       >
//         <Box
//           h="8px"
//           w="100%"
//           bgColor={`brand.${index + 1}`}
//           borderTopRadius="md"
//         />
//         <Box p={2} pl={3}>
//           <HStack justify="flex-end" spacing={1}>
//             <IconButton
//               onClick={onDelete}
//               colorScheme="red"
//               isRound
//               icon={<DeleteIcon />}
//               aria-label={"Delete data point"}
//               size="sm"
//             />
//             <IconButton
//               onClick={onOpen}
//               colorScheme="blue"
//               isRound
//               icon={<EditIcon />}
//               aria-label={"Delete data point"}
//               size="sm"
//             />
//             <IconButton
//               onClick={onDuplicate}
//               colorScheme="green"
//               isRound
//               icon={<CopyIcon />}
//               aria-label={"Duplicate data point"}
//               size="sm"
//             />
//           </HStack>
//           <Heading size="sm">
//             {dataPoint.singleYearTimeframe ?? dataPoint.multiYearTimeframe}
//           </Heading>
//           <Heading size="xs">{getCleanPTName(dataPoint.country)}</Heading>
//           <Box pt={2} display="flex" flexWrap="wrap" gap={1}>
//             {dataPoint.ageGroup && (
//               <Tag size="sm" colorScheme="blue">
//                 <Icon as={BsFillPersonFill} />
//                 {dataPoint.ageGroup}
//               </Tag>
//             )}
//             {dataPoint.sex && (
//               <Tag size="sm" colorScheme="red">
//                 <Icon as={FaGenderless} />
//                 {dataPoint.sex}
//               </Tag>
//             )}
//             {dataPoint.value && (
//               <Tag size="sm" colorScheme="green">
//                 <Icon as={AiOutlineNumber} /> {dataPoint.value}
//               </Tag>
//             )}
//           </Box>
//         </Box>
//       </Box>
//       <AddDataPointModal
//         isOpen={isOpen}
//         onClose={onClose}
//         dataPoints={dataPoints}
//         dataPointIdx={dataPoints.indexOf(dataPoint)}
//         setDataPoints={setDataPoints}
//       />
//     </>
//   );
// }

export function DataPointTable({
  dataPoints,
  setDataPoints,
}: {
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  return (
    <TableContainer w={["100%", "95%", "90%", "85%", "75%"]}>
      <Table variant="simple">
        <TableCaption placement="top">
          <Heading size="md">
            {dataPoints.length} Data Point
            {dataPoints.length === 1 ? "" : "s"}
          </Heading>
        </TableCaption>
        <Thead>
          <Tr>
            <Th isNumeric>#</Th>
            <Th>Actions</Th>
            <Th>Geography</Th>
            <Th>Location</Th>
            <Th isNumeric>Value</Th>
            <Th>Data Quality</Th>
            <Th>Year</Th>
          </Tr>
        </Thead>
        <Tbody>
          {dataPoints.map((dataPoint, idx) => (
            <Tr key={idx}>
              <Td isNumeric>{idx + 1}</Td>
              <Td>
                <HStack spacing={2}></HStack>
              </Td>
              <Td>{dataPoint.geography}</Td>
              <Td>{dataPoint.country}</Td>
              <Td isNumeric>
                {dataPoint.value}
                {dataPoint.valueUnit === "PERCENT" ? " %" : ""}
              </Td>
              <Td>{dataPoint.dataQuality}</Td>
              <Td>
                {dataPoint.singleYearTimeframe ?? dataPoint.multiYearTimeframe}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}
