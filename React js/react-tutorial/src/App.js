import Layout from "./Components/Layout";
import CreateContacts from "./Components/Contacts/create";
import ContactLists from "./Components/Contacts/lists";

function App() {
  return (
    <div className="">
      <Layout/>
       <div className="m-3">
         <CreateContacts />
         <ContactLists/>
       </div>
    </div>
  );
}

export default App;
