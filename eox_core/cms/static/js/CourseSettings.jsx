import React from 'react';
import { InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button } from '@edx/paragon'


export class CourseSettings extends React.Component {

  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {

  }

  handleSubmit(value) {

  }

  render() {
    return (
    <div>
      <div className="row">
        <div className="col-4">
          <InputText
            name="course-regex"
            label="Enter the course regex"
            onSubmit={this.handleSubmit}
          />
          <Button
            label="Find courses"
            name="find"
          ></Button>
        </div>
      </div>
      <div className="row">
        <div className="col-4">
          <RadioButtonGroup
            name="type"
            label=""
          >
            <RadioButton value="deatils">
              Schedule & Details
            </RadioButton>
            <RadioButton value="advanced">
              Advanced Settings
            </RadioButton>
          </RadioButtonGroup>
        </div>
        <div className="col-4">
          <InputSelect
            label="Schedule & Details"
            options={this.props.detailsFields}
            name="details"
          />
        </div>
        <div className="col-4">
          <TextArea name="deatils-value" label="New value" value=""/>
        </div>
      </div>
      <div className="row">
        <div className="col-4">

        </div>
        <div className="col-4">
          <InputSelect
            label="Advanced Settings"
            options={this.props.settingsFields}
            name="advanced"
          />
        </div>
        <div className="col-4">
          <TextArea name="advanced-value" label="New value" value=""/>
        </div>
      </div>
      <Button
        label="Apply changes"
        name="apply"
      ></Button>
    </div>
    );
  }
}