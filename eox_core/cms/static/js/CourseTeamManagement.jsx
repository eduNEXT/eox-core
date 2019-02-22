import React from 'react';
import { InputText, Button, StatusAlert, InputSelect } from '@edx/paragon'
import { clientRequest } from './client'
import { LoadingIconComponent } from './LoadingIcon'
import styles from '../css/CourseTeamManagement'


export class CourseTeamManagement extends React.Component {

  constructor(props) {
    super(props);

    this.apiUrl = '/eox-core/management/course-team-management';

    this.state = {
      org: '',
      user: '',
      role: '',
      isValid: false,
      openAlert: false,
      completedTasks: [],
      failedTasks: [],
      statusAlertMessage: '',
      statusAlertType: '',
      isLoading: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.emailValidator = this.emailValidator.bind(this);
  }

  componentDidMount() {
    this.setState({
      statusAlertMessage: 'Please, enter a valid data.',
      statusAlertType: 'warning'
    });
  }

  handleChange(value, name) {
    if (value !== name) {
      this.setState({
        [name]: value
      });
    }
  }

  handleSubmit(event, role) {
    event.preventDefault();

    if (!this.state.isValid || this.state.org === '') {
      this.openStatusAlert('Please, enter a valid data.', 'danger');
      return;
    }

    let methodType = (role !== '') ? 'POST' : 'DELETE';
    this.setState({
      completedTasks: [],
      failedTasks: [],
      isLoading: true
    });

    clientRequest(
      this.apiUrl,
      methodType,
      {
        'user': this.state.user,
        'org': this.state.org,
        'role': role
      }
    )
    .then(res => res.json())
    .then((response) => {
      if (response.status !== 'Failed')
        this.setStatsLog(response)
      else
        this.apiResponseError(response)
    })
    .catch((error) => {
      console.log(error);
      this.setState({
        isLoading: false
      });
    });
  }

  setStatsLog(response) {
    let completedTasks = response.complete_tasks.map((task) => {
      return <li key={task.course}>
        <p>Task completed for {task.course}</p>
      </li>
    });

    let failedTasks = response.failed_tasks.map((task) => {
      return <li key={task.course}>
        <p>Task was not completed for {task.course} due to: {task.message}</p>
      </li>
    });

    this.setState({
      completedTasks: completedTasks,
      failedTasks: failedTasks,
      isLoading: false
    });
  }

  apiResponseError(response) {
    this.openStatusAlert(response.message, 'danger');
    this.setState({
      isLoading: false
    });
  }

  emailValidator(emailValue) {
    let feedback = { isValid: true };
    const emailRegEx = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (!emailRegEx.test(emailValue)) {
      feedback = {
        isValid: false,
        validationMessage: 'Enter a valid user email.'
      };
      this.setState({
        isValid: false
      });
    } else {
      this.setState({
        isValid: true
      });
    }
    return feedback;
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type
    });
  }

  render() {
    return (
    <div>
      <form onSubmit={this.handleSubmit}>
        <InputText
          id="username"
          name="user"
          label="User email:"
          description="The user email to apply the changes."
          isValid={false}
          onChange={this.handleChange}
          validator={this.emailValidator}
        />
        <InputSelect
          id="org"
          name="org"
          label="Oranization name:"
          description="The org id to add/remove the user."
          onChange={this.handleChange}
          options={this.props.orgList}
        />
        <Button
          label="Add as staff user."
          onClick={(event) => { this.handleSubmit(event, 'staff') }}
          className={['btn-primary']}
        />
        <Button
          label="Add as instructor user."
          onClick={(event) => { this.handleSubmit(event, 'instructor') }}
          className={['btn-primary', styles.btnPrimarySpace]}
        />
        <Button
          label="Remove user."
          onClick={(event) => { this.handleSubmit(event, '') }}
          className={['btn-primary']}
        />
        <StatusAlert
          dialog={this.state.statusAlertMessage}
          onClose={this.onCloseAlert}
          open={this.state.openAlert}
          alertType={this.state.statusAlertType}
        />
      </form>
      <div>
        <h2>Operations complete:</h2>
        <ol>{this.state.completedTasks}</ol>
        <h2>Operations not complete:</h2>
        <ol>{this.state.failedTasks}</ol>
      </div>
      {this.state.isLoading ? <LoadingIconComponent/> : null}
    </div>
    );
  }
}
