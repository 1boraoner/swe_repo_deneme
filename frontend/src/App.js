import "./App.css";
import { Graph } from "react-d3-graph";
import React, { useState } from "react";
import defaultConfig from "./config";
import SearchField from "react-search-field";
import Sidebar from "./Components/Sidebar/sidebar";
import Neo4jDataExample from "./example_data.json";
import neo4jDataToD3Data from "./data_transformer";
import { useEffect } from "react";
import refreshicon from "./Figures/loading.png"

function App() {
  // graph payload (with minimalist structure)
  const [data, setData] = useState({
    nodes: [],
    links: [],
    focusedNodeId: "nodeIdToTriggerZoomAnimation",
  });

  //function to get data from backend server
  async function Request(url, method = ['GET']) {
    const response = await fetch(url, method = method);
    const graphData = await response.json();
    console.log(graphData)
    var formattedGraphData = neo4jDataToD3Data(graphData)
    setData({ ...data, nodes: formattedGraphData.nodes, links: formattedGraphData.relationships })
  }


  //use effect ensures request is sent once
  useEffect(() => {
    Request('http://127.0.0.1:5000/get_graph_data', ['GET']);
  }, [])

  const [nodeData, setNodeData] = useState({});
  const [dataToDisplayDetails, setDataToDisplayDetails] = useState();

  // the graph configuration, just override the ones you need
  const config = Object.assign(defaultConfig);

  const onClickNode = function (nodeId) {
    for (const node of Neo4jDataExample.Nodes) {
      if (node.labels === "Microservice") {
        if (node.properties.name === nodeId) {
          // node is found
          // console.log(node);
          setDataToDisplayDetails(node);
        }
      } else if (node.labels === "Data") {
        if (node.properties.host === nodeId) {
          // node is found
          // console.log(node);
          setDataToDisplayDetails(node);
        }
      }
    }
    setNodeData({ ...nodeData, nodeId: getNodeData(nodeId) });
  };

  const onClickLink = function (source, target) {
    console.log(source, target);
    for (const link of Neo4jDataExample.Relationships) {
      //console.log(link);
      if (link.start_node === source && link.end_node === target) {
        setDataToDisplayDetails(link);
      }
    }
  };

  const onDoubleClickNode = (id, node) => {
    setData({ ...data, focusedNodeId: id });
  };

  const onSearchFieldChange = (searchText) => {
    console.log(searchText);
  };

  const searchFieldSearch = (searchText) => {
    const filterResult = data.nodes.filter((node) => node.id === searchText);
    if (filterResult && filterResult.length !== 0) {
      console.log(filterResult);
      setData({ ...data, focusedNodeId: searchText });
    } else {
      alert("The searched node could not be found.");
    }
  };

  const getNodeData = (nodeId) => {
    return nodeId;
  };

  const refreshGraph = () => {
    Request('http://127.0.0.1:5000/get_graph_data', ['GET']);
  }

  return (
    <div className="App">
      <nav className="navbar">
        <h1>Service Dependency Catalog</h1>
        <div className="links">
          <SearchField
            placeholder="Search a node"
            onChange={onSearchFieldChange}
            searchText=""
            classNames="test-class"
            onEnter={searchFieldSearch}
            onSearchClick={searchFieldSearch}
          />
          <div className="refIconDiv">
            <img classname="refresIcon" src={refreshicon} alt="Refresh Button" onClick={refreshGraph}></img>
          </div>

          {/* <a href="/">Home</a>
          <a
            href="/create"
            style={{
              color: "white",
              backgroundColor: "#f1356d",
              borderRadius: 8,
            }}
          >
            New Blog
          </a> */}
        </div>
      </nav>
      <div className="Page">
        <div className="Graph">
          <Graph
            id="graph-id" // id is mandatory
            data={data}
            config={config}
            onClickNode={onClickNode}
            onClickLink={onClickLink}
            onDoubleClickNode={onDoubleClickNode}
          />
        </div>
        <Sidebar data={dataToDisplayDetails}></Sidebar>
      </div>
    </div>
  );
}

export default App;
