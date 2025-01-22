// import { 
//   Input, 
//   Table, 
//   TableHeader, 
//   TableBody, 
//   TableColumn, 
//   TableRow, 
//   TableCell, 
//   Button, 
//   Card,
//   User,
//   Chip,
//   Dropdown,
//   DropdownTrigger,
//   DropdownMenu,
//   DropdownItem,
//   SortDescriptor
// } from "@nextui-org/react";
// import { SearchIcon, DotsVerticalIcon } from "../components/Icons";
// import { useState, useMemo } from "react";

// interface UserData {
//   id: string;
//   name: string;
//   email: string;
//   avatar?: string;
//   status: 'active' | 'inactive';
//   role: 'admin' | 'user';
//   lastActive: Date;
// }

// // Mock users data
// const mockUsers: UserData[] = Array.from({ length: 20 }, (_, index) => ({
//   id: `USER${String(index + 1).padStart(4, '0')}`,
//   name: [
//     "Josh Smith", "Sarah Wilson", "Michael Brown", "Emma Davis", "James Wilson",
//     "Alice Johnson", "Bob Anderson", "Carol Martinez", "David Thompson", "Eva White"
//   ][Math.floor(Math.random() * 10)],
//   email: `user${index + 1}@example.com`,
//   avatar: `https://i.pravatar.cc/150?u=${index}`,
//   status: Math.random() > 0.2 ? 'active' : 'inactive',
//   role: Math.random() > 0.8 ? 'admin' : 'user',
//   lastActive: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000),
// }));

// export function Users() {
//   const [filterValue, setFilterValue] = useState("");
//   const [sortDescriptor, setSortDescriptor] = useState<SortDescriptor>({
//     column: "lastActive",
//     direction: "descending",
//   });

//   const filteredUsers = useMemo(() => {
//     let filtered = [...mockUsers];

//     if (filterValue) {
//       const lowerFilter = filterValue.toLowerCase();
//       filtered = filtered.filter(user => 
//         user.name.toLowerCase().includes(lowerFilter) ||
//         user.email.toLowerCase().includes(lowerFilter) ||
//         user.id.toLowerCase().includes(lowerFilter)
//       );
//     }

//     return filtered.sort((a, b) => {
//       const { column, direction } = sortDescriptor;
//       let first = a[column as keyof UserData];
//       let second = b[column as keyof UserData];
      
//       if (column === "lastActive") {
//         first = new Date(a.lastActive).getTime();
//         second = new Date(b.lastActive).getTime();
//       }

//       const cmp = first < second ? -1 : first > second ? 1 : 0;

//       return direction === "descending" ? -cmp : cmp;
//     });
//   }, [mockUsers, filterValue, sortDescriptor]);

//   const onSearchChange = (value: string) => {
//     setFilterValue(value);
//   };

//   return (
//     <div className="mt-2 px-12 space-y-8">
//       <Card className="p-6">
//         <div className="flex justify-between items-center mb-6">
//           <div className="space-y-1">
//             <h3 className="text-xl font-semibold">Users</h3>
//             <p className="text-sm text-default-500">Manage your users and their permissions</p>
//           </div>
//           <Button color="primary">Add New User</Button>
//         </div>
        
//         <Input
//           isClearable
//           className="w-full sm:max-w-[44%]"
//           placeholder="Search by name, email, or user ID..."
//           startContent={<SearchIcon />}
//           value={filterValue}
//           onClear={() => setFilterValue("")}
//           onValueChange={onSearchChange}
//         />
//       </Card>

//       <Table 
//         aria-label="Users table"
//         sortDescriptor={sortDescriptor}
//         onSortChange={setSortDescriptor}
//       >
//         <TableHeader>
//           <TableColumn key="name" allowsSorting>User</TableColumn>
//           <TableColumn key="role" allowsSorting>Role</TableColumn>
//           <TableColumn key="status" allowsSorting>Status</TableColumn>
//           <TableColumn key="lastActive" allowsSorting>Last Active</TableColumn>
//           <TableColumn>Actions</TableColumn>
//         </TableHeader>
//         <TableBody>
//           {filteredUsers.map((user) => (
//             <TableRow key={user.id}>
//               <TableCell>
//                 <User
//                   name={user.name}
//                   description={user.email}
//                   avatarProps={{
//                     src: user.avatar,
//                     fallback: user.name.charAt(0),
//                     size: "sm"
//                   }}
//                 />
//               </TableCell>
//               <TableCell>
//                 <Chip
//                   className="capitalize"
//                   color={user.role === 'admin' ? 'warning' : 'default'}
//                   size="sm"
//                   variant="flat"
//                 >
//                   {user.role}
//                 </Chip>
//               </TableCell>
//               <TableCell>
//                 <Chip
//                   className="capitalize"
//                   color={user.status === 'active' ? 'success' : 'danger'}
//                   size="sm"
//                   variant="flat"
//                 >
//                   {user.status}
//                 </Chip>
//               </TableCell>
//               <TableCell>
//                 {user.lastActive.toLocaleDateString()}
//               </TableCell>
//               <TableCell>
//                 <Dropdown>
//                   <DropdownTrigger>
//                     <Button 
//                       isIconOnly 
//                       size="sm" 
//                       variant="light"
//                     >
//                       <DotsVerticalIcon />
//                     </Button>
//                   </DropdownTrigger>
//                   <DropdownMenu>
//                     <DropdownItem>Edit</DropdownItem>
//                     <DropdownItem>View Details</DropdownItem>
//                     <DropdownItem
//                       className="text-danger"
//                       color="danger"
//                     >
//                       Deactivate
//                     </DropdownItem>
//                   </DropdownMenu>
//                 </Dropdown>
//               </TableCell>
//             </TableRow>
//           ))}
//         </TableBody>
//       </Table>
//     </div>
//   );
// } 