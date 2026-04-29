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
  
  // Edit variables
  newDental: string = '';
  newVision: string = '';
  newMedical: string = '';

  async search() {
    if (!this.employeeId) return;
    try {
      const res = await fetch('http://localhost:3000/api/employee/' + this.employeeId);
      this.employeeData = await res.json();
      
      if (this.employeeData && !this.employeeData.error) {
        this.newDental = this.employeeData.dental_plan;
        this.newVision = this.employeeData.vision_plan;
        this.newMedical = this.employeeData.medical_plan;
      }
    } catch (e) {
      console.error("Error fetching employee:", e);
    }
  }

  async update() {
    if (!this.employeeData || this.employeeData.error) return;
    try {
      await fetch('http://localhost:3000/api/employee/' + this.employeeId + '/benefits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          dental_plan: this.newDental,
          vision_plan: this.newVision,
          medical_plan: this.newMedical
        })
      });
      await this.search();
    } catch (e) {
      console.error("Error updating benefits:", e);
    }
  }
}
