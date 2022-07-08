import {
  VStack,
  Text,
  Box,
  Heading,
  ButtonGroup,
  Button,
  HStack,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { ColorModeSwitcher } from "../ColorModeSwitcher";
import { Page } from "./Page";
import {
  AddIcon,
  AttachmentIcon,
  DownloadIcon,
  EditIcon,
} from "@chakra-ui/icons";

export function HomePage() {
  let navigate = useNavigate();
  const pages = [
    {
      title: "Add Indicator",
      path: "/add-indicator",
      icon: <AddIcon />,
    },
    {
      title: "Past Submissions",
      path: "/past-submissions",
      icon: <EditIcon />,
    },
    {
      title: "Import File",
      path: "/import",
      icon: <AttachmentIcon />,
    },
    {
      title: "Export Data",
      path: "/export",
      icon: <DownloadIcon />,
    },
  ];
  return (
    <Page
      title="CPHO Phase 2"
      subTitle="Data Collection and Retrieval Application"
    >
      <VStack py={10} justify="center" spacing={6}>
        {pages.map(({ title, path, icon }) => (
          <Button
            key={title}
            leftIcon={icon}
            fontSize={22}
            size="lg"
            onClick={() => navigate(path)}
          >
            {title}
          </Button>
        ))}
      </VStack>
    </Page>
  );
}
