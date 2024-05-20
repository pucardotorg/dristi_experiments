// import IndexPage from "../pages/index";
import IndexPage from "@/pages/indexPage"

export default function Home() {
  return (
    <div>
      <h1
        style={{
          display: "flex",
          justifyContent: "center",
          fontSize: "40px",
          fontWeight: "normal",
          color: "#3399ff",
          marginBottom: "2px",
        }}
      >
        Dristi Experiments
      </h1>
      <IndexPage />
    </div>
  )
}
