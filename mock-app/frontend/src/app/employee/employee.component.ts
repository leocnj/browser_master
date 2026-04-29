import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-employee',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './employee.component.html',
  styleUrl: './employee.component.css'
})
export class EmployeeComponent {
  employeeId: string = '';
  employeeData: any = null;
  newDental: string = '';

  async search() {
    const res = await fetch('http://localhost:3000/api/employee/' + this.employeeId);
    this.employeeData = await res.json();
  }

  async update() {
    await fetch('http://localhost:3000/api/employee/' + this.employeeId + '/dental', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dental: this.newDental })
    });
    this.search();
  }
}
