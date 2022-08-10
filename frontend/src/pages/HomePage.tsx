import { VStack, Button } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
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
      title: "New Indicator",
      path: "/add-indicator",
      icon: <AddIcon />,
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
    // {
    //   title: "Past Submissions",
    //   path: "/past-submissions",
    //   icon: <EditIcon />,
    // },
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
            fontWeight={500}
            size="lg"
            onClick={() => navigate(path)}
            disabled={title === "Past Submissions"}
          >
            {title}
          </Button>
        ))}
      </VStack>
    </Page>
  );
}
