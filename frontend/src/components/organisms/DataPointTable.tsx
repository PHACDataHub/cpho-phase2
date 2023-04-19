import { Table, TableContainer, Tbody, Th, Thead, Tr } from "@chakra-ui/react";
import { useContext } from "react";
import IndicatorFormContext from "../../utils/context/IndicatorFormContext";
import DataPointRow from "./DataPointRow";

export function DataPointTable() {
  const { indicator } = useContext(IndicatorFormContext);

  return (
    <TableContainer w={["100%", "95%", "90%", "85%", "75%"]}>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th isNumeric>#</Th>
            <Th>Actions</Th>
            <Th>Geography</Th>
            <Th>Location</Th>
            <Th isNumeric>Value</Th>
            <Th>Unit</Th>
            <Th>Data Quality</Th>
            <Th>Year</Th>
          </Tr>
        </Thead>
        <Tbody>
          {indicator?.indicatordataSet.map((dataPoint) => (
            <DataPointRow key={dataPoint.id} dataPoint={dataPoint} />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}
