import { AddIcon, MinusIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  ButtonGroup,
  Center,
  Heading,
  HStack,
  IconButton,
  Text,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { Page } from "./Page";
import { RiFileExcel2Fill } from "react-icons/ri";
import { FaFileCsv } from "react-icons/fa";
import { ImDatabase } from "react-icons/im";
import { useSmallScreen } from "../utils/hooks";
import { writer } from "repl";

const PossibleIndicatorCard = ({
  indicator: { name, dataPointCount, id },
  addSelected,
  removeSelected,
}: {
  indicator: { id: number; name: string; dataPointCount: number };
  addSelected: (id: number) => void;
  removeSelected: (id: number) => void;
}) => {
  const [selected, setSelected] = useState(false);

  useEffect(() => {
    if (selected) {
      addSelected(id);
    } else {
      removeSelected(id);
    }
  }, [selected, id, addSelected, removeSelected]);

  return (
    <Box
      flexGrow={1}
      p={4}
      borderRadius="md"
      minW="200px"
      bgColor={selected ? "gray.400" : "gray.200"}
      transition="all 0.2s ease-in-out"
    >
      <Box w="100%" display="flex" flexDir="row" justifyContent="space-between">
        <Heading size="sm">{name}</Heading>
        <IconButton
          onClick={() => setSelected(!selected)}
          isRound
          size="sm"
          aria-label="Add indicator to export"
          icon={selected ? <MinusIcon /> : <AddIcon />}
        />
      </Box>
      <Heading size="sm" fontWeight="normal" fontStyle="italic">
        {dataPointCount} data point{dataPointCount === 1 ? "" : "s"}
      </Heading>
    </Box>
  );
};

export function ExportPage() {
  const toast = useToast();
  const [fileType, setFileType] = useState<"excel" | "csv" | "sql">("csv");
  const [possibleIndicators, setPossibleIndicators] = useState<
    { id: number; name: string; dataPointCount: number }[]
  >([]);

  const isSmallScreen = useSmallScreen();

  const [selectedIndicators, setSelectedIndicators] = useState<number[]>([]);
  const [csvText, setCsvText] = useState("");

  const addSelected = (indicatorId: number) => {
    if (!selectedIndicators.includes(indicatorId)) {
      setSelectedIndicators([...selectedIndicators, indicatorId]);
      if (csvText) setCsvText("");
    }
  };

  const removeSelected = (indicatorId: number) => {
    if (selectedIndicators.includes(indicatorId)) {
      const idx = selectedIndicators.indexOf(indicatorId);
      setSelectedIndicators(
        selectedIndicators
          .slice(0, idx)
          .concat(selectedIndicators.slice(idx + 1))
      );
      if (csvText) setCsvText("");
    }
  };

  useEffect(() => {
    fetch(
      (process.env.REACT_APP_SERVER_URL || "http://localhost:8000/") +
        "api/possibleindicators",
      {
        method: "GET",
      }
    )
      .then(async (res) => {
        const obj = await res.json();
        setPossibleIndicators(obj);
        console.log(obj);
      })
      .catch((err) => {
        console.log("ERROR", err);
      });
  }, []);

  const handleExport = () => {
    const formData = new FormData();
    formData.append("selectedIndicators", JSON.stringify(selectedIndicators));
    fetch(
      (process.env.REACT_APP_SERVER_URL || "http://localhost:8000/") +
        "api/export",
      {
        method: "POST",
        body: formData,
      }
    )
      .then(async (res) => {
        const obj = await res.text();
        setCsvText(obj);
        console.log(obj);
      })
      .catch((err) => {
        console.log("ERROR", err);
      });
  };

  const exportCsv = () => {
    if(csvText){
      const blob = new Blob([csvText], {type: "text/csv;charset=utf-8"});
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", "data.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast({
        title: "Data Downloaded",
        description: "The data you requested has been downloaded to your computer",
        status: "success",
        duration: 4000,
        isClosable: true,
      })
    }
  };

  return (
    <Page title="Export Data" backButton={{ show: true, redirectUrl: "/" }}>
      <VStack spacing={8}>
        <Box
          w={isSmallScreen ? "95%" : "70%"}
          my={3}
          mb={10}
          display="flex"
          flexWrap="wrap"
          gap={3}
          alignContent="flex-start"
        >
          {possibleIndicators.map((ind) => (
            <PossibleIndicatorCard
              addSelected={addSelected}
              removeSelected={removeSelected}
              key={ind.id}
              indicator={ind}
            />
          ))}
        </Box>
        <ButtonGroup size="lg" isAttached>
          <Button
            leftIcon={<FaFileCsv />}
            fontSize="2xl"
            isActive={fileType === "csv"}
            onClick={() => setFileType("csv")}
          >
            CSV
          </Button>
          <Button
            leftIcon={<RiFileExcel2Fill color="green" />}
            fontSize="2xl"
            isActive={fileType === "excel"}
            onClick={() => setFileType("excel")}
            isDisabled
          >
            Excel
          </Button>
        </ButtonGroup>
        {selectedIndicators.length > 0 && (
          <>
            <Heading size="md">
              You are about to export the following data:
            </Heading>
            {selectedIndicators.map((ind) => (
              <Heading key={ind} size="sm">
                {possibleIndicators.find((i) => i.id === ind)?.name}
              </Heading>
            ))}
          </>
        )}
        <Button
          cursor="pointer"
          colorScheme="green"
          w="60%"
          as="a"
          download
          isDisabled={selectedIndicators.length < 1}
          onClick={handleExport}
        >
          Get Data
        </Button>
        {csvText && <Text>Your data is ready! Click <Button onClick={exportCsv} variant="link">here</Button> to download</Text>}
      </VStack>

    </Page>
  );
}
